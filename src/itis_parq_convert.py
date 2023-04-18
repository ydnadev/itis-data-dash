import pandas as pd

df = pd.read_csv('../itisdata/animals_phyla.txt', sep='\t')
df.to_parquet('../data/itis.parquet')
df = pd.read_csv('../itisdata/animal_vernacular.csv')
df.to_parquet('../data/itis_vernacular.parquet')
