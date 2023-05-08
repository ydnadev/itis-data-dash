import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

# Streamlit config
st.set_page_config(
    page_title = 'ITIS Lookup',
    layout = 'wide',
)
pd.set_option('display.max_rows',None)

#CSV convert def
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Main app
st.header('ITIS Taxa Lookup')
st.write('Data from Integrated Taxonomic Information System (ITIS) - https://www.itis.gov/')
st.write('data load date: :blue[26-Apr-2023]')

# Get data from parquet file for vernacular names
def get_data() -> pd.DataFrame:
    return pd.read_parquet('data/itis_vernacular.parquet')
cn = get_data()

# Get data from parquet file for species data
def get_data() -> pd.DataFrame:
    return pd.read_parquet('data/itis.parquet')
df = get_data()


## Search by Common name
# free search box, return sci and vern names sorted by vern name
st.write(':orange[Note: Scientific name =  complete_name, Common name = vernacular_name]') 
text_search = st.text_input('Find species by name (e.g. polar bear or *Ursus maritimus*):', value = '')
search_sp = cn['complete_name'].str.contains(text_search, case=False)
search_cn = cn['vernacular_name'].str.contains(text_search, case=False)
df_search = cn[search_sp | search_cn]
#df_search['scientific_name'] = df_search['complete_name']
df_return = df_search[['tsn','complete_name','vernacular_name']]
df_return['vernacular_name_upper'] = df_return['vernacular_name'].str.upper()
df_return = df_return.sort_values(by=['vernacular_name_upper'])
df_return['tsn'] = df_return['tsn'].astype(str)
del df_return['vernacular_name_upper']
if text_search:
    st.dataframe(df_return,use_container_width=True)
    #<--

    ## Download CSV button
    csv = convert_df(df_return)
    st.download_button(
        label='Download data as CSV',
        data=csv,
        file_name = 'itis_vernacular-' + text_search + '.csv',
        mime='text/csv',
    )

st.markdown('''---''')

## Search by Species
species_search = st.text_input('Species search (e.g. *Ursus maritimus*)', value = '')
try:
    species_search = species_search.upper()
    print(species_search)
    search_species = df[df['complete_name'].str.upper() == species_search]
    if not search_species['tsn'].isnull().values.any():
        itis_link = 'https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=' + search_species['tsn'].values[0].astype(str) + ''
        st.write(search_species['name_usage'].values[0] + ' -- ' + itis_link)
        #itis_link = search_species['tsn'].values[0].astype(str)
    if not search_species['kingdom'].isnull().values.any():
        st.write('KINGDOM - ' + search_species['kingdom'].values[0])
    if not search_species['subkingdom'].isnull().values.any():
        st.write('SUBKINGDOM - ' + search_species['subkingdom'].values[0])
    if not search_species['phylum'].isnull().values.any():
        st.write('----- PHYLUM - ' + search_species['phylum'].values[0])
    if not search_species['subphylum'].isnull().values.any():
        st.write('----- SUBPHYLUM - ' + search_species['subphylum'].values[0])
    if not search_species['class'].isnull().values.any():
        st.write('----- ----- CLASS - ' + search_species['class'].values[0])
    if not search_species['superorder'].isnull().values.any():
        st.write('----- ----- ----- SUPERORDER - ' + search_species['superorder'].values[0])
    if not search_species['order'].isnull().values.any():
        st.write('----- ----- ----- ORDER - ' + search_species['order'].values[0])
    if not search_species['suborder'].isnull().values.any():
        st.write('----- ----- ----- SUBORDER - ' + search_species['suborder'].values[0])
    if not search_species['superfamily'].isnull().values.any():
        st.write('----- ----- ----- ----- SUPERFAMILY - ' + search_species['superfamily'].values[0])
    if not search_species['family'].isnull().values.any():
        st.write('----- ----- ----- ----- FAMILY - ' + search_species['family'].values[0])
    if not search_species['subfamily'].isnull().values.any():
        st.write('----- ----- ----- ----- SUBFAMILY - ' + search_species['subfamily'].values[0])
except:
    st.write('please try again')

st.markdown('''---''')



## Search by Genus
ge_search = st.text_input('Enter Genus (e.g. *Ursus*)', value = '')
ge_search = ge_search.title()
placeholder = st.empty()
search_ge = df[df['unit_name1'] == ge_search]
#search_ge = df[df['unit_name1'].str.contains(ge_search, case=False)]
df2 = search_ge.sort_values(by=['complete_name'])

## Dataframe based on Genus
df1 = df2[['tsn','name_usage','complete_name','subfamily','family','superfamily','suborder','order','superorder','class','subphylum','phylum','subkingdom','kingdom']]
def color_vald(val):
    color = 'green' if val == 'valid' or val == 'accepted' else ''
    return f'background-color: {color}'
if ge_search:
    st.dataframe(df1.style.applymap(color_vald, subset=['name_usage']), use_container_width=True)

    ## Download CSV button
    csv2 = convert_df(df1)
    st.download_button(
        label='Download data as CSV',
        data=csv2,
        file_name = 'itis_data-' + ge_search + '.csv',
        mime='text/csv',
    )

st.markdown('''---''')

st.write('Github - https://github.com/ydnadev/itis-data-dash')
