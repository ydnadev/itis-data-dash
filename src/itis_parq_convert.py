import pandas as pd

df1 = pd.read_csv('../itisdata/species_taxa.txt', sep='\t')
df1.to_parquet('../data/itis.parquet')
df2 = pd.read_csv('../itisdata/species_vernacular.csv')
df2.to_parquet('../data/itis_vernacular.parquet')
df3 = pd.read_csv('../itisdata/geographic.csv')
df3.to_parquet('../data/itis_geographic.parquet')
