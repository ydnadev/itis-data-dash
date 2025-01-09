import duckdb as dk
import pandas as pd

df1 = pd.read_csv('../itisdata/species_taxa.txt', sep='\t')
df1.to_parquet('../data/itis.parquet')
con1 = dk.connect('../data/itis.duckdb')
con1.sql("create table itis as select * from read_parquet('../data/itis.parquet')")
con1.close()
df2 = pd.read_csv('../itisdata/species_vernacular.csv')
df2.to_parquet('../data/itis_vernacular.parquet')
con2 = dk.connect('../data/itis.duckdb')
con2.sql("create table itis_vernacular as select * from read_parquet('../data/itis_vernacular.parquet')")
con2.close()
df3 = pd.read_csv('../itisdata/geographic.csv')
df3.to_parquet('../data/itis_geographic.parquet')
con3 = dk.connect('../data/itis.duckdb')
con3.sql("create table itis_geographic as select * from read_parquet('../data/itis_geographic.parquet')")
con3.close()
