import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

# Streamlit config
st.set_page_config(
    page_title = 'ITIS Lookup',
    layout = 'wide',
)
pd.set_option('display.max_rows',None)

# Main app
st.header('ITIS Taxa Lookup - Animals')
st.write('Data from Integrated Taxonomic Information System (ITIS) - https://www.itis.gov/')
st.write('data load date: 30-Mar-2023')

# Get data from parquet file
def get_data() -> pd.DataFrame:
    return pd.read_parquet('data/itis_vernacular.parquet')
cn = get_data()

## Search by Common name
#cn_filter = st.text_input('Common name')
#cn_filter = cn_filter.title()
st.write('To edit- click in box, use :green[backspace] to delete, then type or paste...')
cn_filter = st.selectbox('Select/Type the Common Name to Search Species', pd.unique(cn['vernacular_name']))
placeholder1 = st.empty()
cn = cn[cn['vernacular_name'] == cn_filter]
cn = cn.sort_values(by=['complete_name'])
st.table(cn)

# Get data from parquet file
def get_data() -> pd.DataFrame:
    return pd.read_parquet('data/itis.parquet')
df = get_data()

st.markdown("""---""")

## Search by Genus
sp_filter = st.text_input('Type the Genus to Search')
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

