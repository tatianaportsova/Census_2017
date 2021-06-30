
# Census_2017 is a project where a new table is built based on the information from the [source dataset](https://www.kaggle.com/muonneutrino/us-census-demographic-data?select=acs2017_census_tract_data.csv)


### [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) is used to load and write queries to explore the data, and populate the following columns of the new table:

∙ State

∙ Count of Census Tracts

∙ Total State Population

∙ Most Populous County

∙ Population of the Most Populous County

∙ County with Highest Percentage of Non-White Residents

∙ Population of that County

∙ Percentage of White Residents in that County

∙ Percentage of Non-White Residents in that County

∙ Percentage of Male Residents in that County

∙ Percentage of Female Residents in that County

∙ Majority Race in that County 

∙ Statistically-Generated Estimate of Count of Males of Majority Race in that County

∙ Statistically-Generated estimate of Count of Females of Majority Race in that County

## ____________________________________________________________
## Please note that since the source dataset contains missing values, the derived columns of the new dataset are converted to NULL as well in order to avoid incorrect misleading calculations.

