import os
import sqlite3
import pandas


df = pandas.read_csv("data/acs2017_census_tract_data.csv")
conn = sqlite3.connect("2017_census_data.sqlite3")
curs = conn.cursor()
df.to_sql('users', conn, if_exists='replace',
           index=False)
