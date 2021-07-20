import os
import sqlite3

# Construct a path to the Source Database 
DB_FILEPATH1  = os.path.join(os.path.dirname(__file__), "2017_census_data.sqlite3")

# Open the Database connection
connection1 = sqlite3.connect(DB_FILEPATH1)
connection1.row_factory = sqlite3.Row
# print("CONNECTION:", connection1)
# Declare a cursor
cursor1 = connection1.cursor()


# --------------- Main Query --------------- #
# The Main Query that creates and populates the new Table

MainQ = """
    CREATE TABLE IF NOT EXISTS Census_Table AS 
    SELECT 
      DISTINCT users.State AS State, 
      COUNT(TractId) AS Census_Tracts_Count,
      SUM(TotalPop) AS Total_State_Population,
      hV.County AS Most_Populated_County,
      hV.T_Pop AS MPC_Population,
      hV1.County AS County_Highest_Percentage_of_Non_White,
      hV1.Total_Pop AS Non_White_County_Population,
      hV2.White_Pop AS White_Percentage,
      ROUND(100-(hV2.White_Pop),2) AS Non_White_Percentage,
      ROUND(CAST(hV1.Men AS Float)/(CAST(hV1.Total_Pop AS Float)/100),2) AS Percentage_Male,
      ROUND(CAST(hV1.Women AS Float)/(CAST(hV1.Total_Pop AS Float)/100),2)AS Percentage_Female,
      hV4.Majority_Race AS Majority_Race,
      CAST (ROUND(hV5.RacePopulation_Men,0) AS INT) AS Estimate_Count_Males,
      CAST (ROUND(hV5.RacePopulation_Women,0) AS INT) AS Estimate_Count_Females
    FROM users
    LEFT JOIN helper_View AS hV ON hV.State=users.State
    LEFT JOIN helper_View1 AS hV1 ON hV1.State=users.State
    LEFT JOIN helper_View2 AS hV2 ON hV2.State=users.State
    LEFT JOIN helper_View4 AS hV4 ON hV4.State=users.State
    LEFT JOIN helper_View5 AS hV5 ON hV5.State=users.State
    GROUP BY users.State;
    """

# --------------- Helper Queries --------------- #
# A View is a result set of a stored query. 
# A view is the way to pack a query into a named object stored in the database.
# The data of the underlying tables can be accesses through a view. 

# helper_View stores the names and populations of the most populated counties in each state
helperQ = """
        CREATE VIEW IF NOT EXISTS helper_View AS
        WITH county_Pop AS (
        SELECT
            State,
            County,
            SUM(TotalPop) AS T_pop
        FROM users
        GROUP BY
            State,
            County),
        max_Pop AS (
        SELECT
            State,
            County,
            T_Pop,
            ROW_NUMBER() OVER(PARTITION BY State ORDER BY T_pop DESC) AS row_number
        FROM county_Pop)
        SELECT * FROM max_Pop WHERE row_number = 1;
        """

# helper_View1 stores the names and populations of the counties
# with the highest percentage of non-white residents in each state,
# number of men, number of women in that county,
# information on percentages of other races in that county
helperQ1 = """
          CREATE VIEW IF NOT EXISTS helper_View1 AS
          SELECT * FROM (
            WITH added_row_number AS (
              SELECT *, 
                    ROW_NUMBER() OVER(PARTITION BY State ORDER BY White_Pop ASC) AS row_number
                    FROM (
                    SELECT 
                      COUNT(*) AS Number_Tract, 
                      SUM(TotalPop) AS Total_Pop, 
                      State, County,
                      SUM(Hispanic) AS Hispanic_Pop,  
                      SUM(Black) AS Black_Pop, 
                      SUM(Native) AS Native_Pop, 
                      SUM(Asian) AS Asian_Pop, 
                      SUM(Pacific) AS Pacific_Pop,
                      SUM(White) AS White_Pop,
                      SUM(Men) AS Men, 
                      SUM(Women) AS Women 
                    FROM users
                    GROUP BY State, County 
                    ORDER BY State, White_Pop ASC) AS n_Table) 
            SELECT * FROM added_row_number
            WHERE row_number = 1);        
          """

# helper_View2 stores the information on percentage of White people 
# in the counties with the highest percentage of non-white residents in each state
helperQ2 = """
      CREATE VIEW IF NOT EXISTS helper_View2 AS 
      SELECT 
        State, 
        County, 
        ROUND(White_Pop/Number_Tract,2) AS White_Pop 
      FROM helper_View1;
      """

# helper_View4 stores name of the Majority Race for the counties
# with the highest percentage of non-white residents in each state
helperQ4 = """
          CREATE VIEW IF NOT EXISTS helper_View4 AS 
          SELECT
            State,
            County,
          CASE
          WHEN Hispanic_Pop > Black_Pop
              AND Hispanic_Pop > Native_Pop
              AND Hispanic_Pop > Asian_Pop
              AND Hispanic_Pop > Pacific_Pop
              AND Hispanic_Pop > White_Pop
            THEN 'Hispanic'
          WHEN Black_Pop > Hispanic_Pop
              AND Black_Pop > Native_Pop
              AND Black_Pop > Asian_Pop
              AND Black_Pop > Pacific_Pop
              AND Black_Pop > White_Pop
            THEN 'Black'
          WHEN Native_Pop > Hispanic_Pop
              AND Native_Pop > Black_Pop
              AND Native_Pop > Asian_Pop
              AND Native_Pop > Pacific_Pop
              AND Native_Pop > White_Pop
            THEN 'Native'
          WHEN Asian_Pop > Hispanic_Pop
              AND Asian_Pop > Black_Pop
              AND Asian_Pop > Native_Pop
              AND Asian_Pop > Pacific_Pop
              AND Asian_Pop > White_Pop
            THEN 'Asian'
          WHEN Pacific_Pop > Hispanic_Pop
              AND Pacific_Pop > Black_Pop
              AND Pacific_Pop > Native_Pop
              AND Pacific_Pop > Asian_Pop
              AND Pacific_Pop > White_Pop
            THEN 'Pacific'
          WHEN White_Pop > Hispanic_Pop
              AND White_Pop > Black_Pop
              AND White_Pop > Native_Pop
              AND White_Pop > Asian_Pop
              AND White_Pop > Pacific_Pop
            THEN 'White'
          END AS Majority_Race
          FROM helper_View1;
          """

# helper_View5 estimates the number of Male and Female residents for the counties
# with the highest percentage of non-white residents in each state
# that belong to the Majority Race in that county
helperQ5 = """
          CREATE VIEW IF NOT EXISTS helper_View5 AS 
          SELECT
            hV1.State,
            hV1.County,
            ((((CAST (hV.T_Pop AS Float)/100)*(SELECT ROUND(MAX(hV1.Hispanic_Pop, 
                              hV1.Black_Pop, 
                              hV1.Native_Pop, 
                              hV1.Asian_Pop, 
                              hV1.Pacific_Pop, 
                              hV1.White_Pop),1)/CAST (hV1.Number_Tract AS Float)))/100)*ROUND(CAST (hV1.Men AS Float)/(CAST (hV1.Total_Pop AS Float)/100),2)) AS RacePopulation_Men,
            ((((CAST (hV.T_Pop AS Float)/100)*(SELECT ROUND(MAX(hV1.Hispanic_Pop, 
                              hV1.Black_Pop, 
                              hV1.Native_Pop, 
                              hV1.Asian_Pop, 
                              hV1.Pacific_Pop, 
                              hV1.White_Pop),1)/CAST (hV1.Number_Tract AS Float)))/100)*ROUND(CAST (hV1.Women AS Float)/(CAST (hV1.Total_Pop AS Float)/100),2)) AS RacePopulation_Women
          FROM helper_View1 AS hV1
          LEFT JOIN helper_View AS hV ON hV.State=hv1.State
          """

# Execute the Helper Queries
cursor1.execute(helperQ)
cursor1.execute(helperQ1)
cursor1.execute(helperQ2)
cursor1.execute(helperQ4)
cursor1.execute(helperQ5)

# Execute the Main Query
cursor1.execute(MainQ)

# Commit & Close the connection to the Database
connection1.commit()
connection1.close()

print("Census_Table has been created")



