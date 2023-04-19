import pandas as pd

df = pd.read_csv('../itisdata/species_taxa.txt', sep='\t')
df.to_parquet('../data/itis.parquet')
df = pd.read_csv('../itisdata/species_vernacular.csv')
df.to_parquet('../data/itis_vernacular.parquet')
