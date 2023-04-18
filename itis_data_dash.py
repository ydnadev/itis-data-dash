import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

# Streamlit config
st.set_page_config(
    page_title = 'ITIS Lookup',
    layout = 'wide',
)
pd.set_option('display.max_rows',None)

# Get data from parquet file
def get_data() -> pd.DataFrame:
    return pd.read_parquet('data/itis.parquet')
df = get_data()

# Main app
st.header('ITIS Taxa Lookup')
st.write('Data from Integrated Taxonomic Information System (ITIS) - https://www.itis.gov/')
st.write('data load date: 30-Mar-2023')

## Search by Genus
sp_filter = st.text_input('Genus')
sp_filter = sp_filter.title()
placeholder = st.empty()
df = df[df['unit_name1'] == sp_filter]
df = df.sort_values(by=['complete_name'])

## Dataframe based on Genus
df1 = df[['complete_name','name_usage','subkingdom','phylum','subphylum','superclass','class','subclass','infraclass','superorder','order','suborder','infraorder','section','subsection','superfamily','family','subfamily','tribe','subtribe','unaccept_reason']]
def color_vald(val):
    color = 'blue' if val == 'valid' else ''
    return f'background-color: {color}'
st.dataframe(df1.style.applymap(color_vald, subset=['name_usage']), use_container_width=True)


## Download CSV button
def convert_df(df):
    return df.to_csv().encode('utf-8')
csv = convert_df(df1)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name = sp_filter + 'itis_data.csv',
    mime='text/csv',
)

