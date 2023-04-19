import pandas as pd
import pyarrow.parquet as pq
import streamlit as st
import numpy as np

# Streamlit config
st.set_page_config(
    page_title = 'ITIS Lookup',
    layout = 'wide',
)
pd.set_option('display.max_rows',None)

# Main app
st.header('ITIS Taxa Lookup')
st.write('Data from Integrated Taxonomic Information System (ITIS) - https://www.itis.gov/')
st.write('data load date: :blue[30-Mar-2023]')

# Get data from parquet file for vernacular names
def get_data() -> pd.DataFrame:
    return pd.read_parquet('data/itis_vernacular.parquet')
cn = get_data()

## Search by Common name
# free search box, return sci and vern names sorted by vern name
st.write(':orange[Note: Scientific name =  complete_name, Common name = vernacular_name]') 
text_search = st.text_input('Find species by name:', value = '')
search_sp = cn['complete_name'].str.contains(text_search, case=False)
search_cn = cn['vernacular_name'].str.contains(text_search, case=False)
df_search = cn[search_sp | search_cn]
#df_search['scientific_name'] = df_search['complete_name']
df_return = df_search[['complete_name','vernacular_name']]
df_return['vernacular_name_upper'] = df_return['vernacular_name'].str.upper()
df_return = df_return.sort_values(by=['vernacular_name_upper'])
del df_return['vernacular_name_upper']
if text_search:
    st.dataframe(df_return,use_container_width=True)
    #<--

# Get data from parquet file for species data
def get_data() -> pd.DataFrame:
    return pd.read_parquet('data/itis.parquet')
df = get_data()

st.markdown('''---''')

## Search by Genus
ge_search = st.text_input('Enter Genus', value = '')
ge_search = ge_search.title()
placeholder = st.empty()
search_ge = df[df['unit_name1'] == ge_search]
#search_ge = df[df['unit_name1'].str.contains(ge_search, case=False)]
df2 = search_ge.sort_values(by=['complete_name'])

## Dataframe based on Genus
df1 = df2[['complete_name','name_usage','subkingdom','phylum','subphylum','superclass','class','subclass','infraclass','superorder','order','suborder','infraorder','section','subsection','superfamily','family','subfamily','tribe','subtribe','unaccept_reason']]
def color_vald(val):
    color = 'blue' if val == 'valid' or val == 'accepted' else ''
    return f'background-color: {color}'
st.dataframe(df1.style.applymap(color_vald, subset=['name_usage']), use_container_width=False)


## Download CSV button
def convert_df(df):
    return df.to_csv().encode('utf-8')
csv = convert_df(df1)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name = ge_search + '_itis_data.csv',
    mime='text/csv',
)

