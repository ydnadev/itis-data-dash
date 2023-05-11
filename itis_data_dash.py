import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyarrow.parquet as pq
import streamlit as st
from fastparquet import ParquetFile

# Streamlit config
st.set_page_config(
    page_title = 'ITIS Lookup',
    layout = 'wide',
)
pd.set_option('display.max_rows',None)

#CSV convert def
def convert_df(df):
    return df.to_csv().encode('utf-8')

#get data from parquet file
def get_data(f) -> pd.DataFrame:
    return pd.read_parquet(f)

# Main app
st.header('ITIS Taxa Lookup')
st.write('Data from Integrated Taxonomic Information System (ITIS) - https://www.itis.gov/')
st.write('data load date: :blue[26-Apr-2023]')
st.write('TSN -- Taxonomic Serial Number')

# Get data from parquet file for vernacular names
its_vern = 'data/itis_vernacular.parquet'
cn = get_data(its_vern)

# Get data from parquet file for species data
itis_spec = 'data/itis.parquet'
df = get_data(itis_spec)

# Get data from parquet file for geographics values
geo = 'data/itis_geographic.parquet'
gd = ParquetFile(geo)
ll = pd.read_csv('data/lat_long.csv')

st.write('---')

# Summation charts
with st.expander("Groupings by Taxa"):
    c1,c2,c3 = st.columns(3)
    with c2:
        fig_king = go.Figure()
        fig_king.add_trace(go.Bar(
            x = df['kingdom'].value_counts(),
            y = df['kingdom'].value_counts().index,
            marker = dict(color = 'crimson'),
            orientation = 'h'
        ))
        fig_king.update_layout(
            title='ITIS TSN by Kingdom',
            yaxis = dict(autorange = 'reversed'),
            xaxis_title = 'TSN count',
            plot_bgcolor = '#dbdbdb'
        )
        fig_king.update_yaxes(gridcolor = 'white')
        st.plotly_chart(fig_king)
    king_filter = st.selectbox("Select the Kingdom", pd.unique(df["kingdom"].sort_values()))

    if king_filter:
        kingf = df[df["kingdom"] == king_filter]

        colf1, colf2 = st.columns(2)
        colf3, colf4 = st.columns(2)
        
        with colf1:
            fig_phyl = go.Figure()
            fig_phyl.add_trace(go.Bar(
                x = kingf['phylum'].value_counts(),
                y = kingf['phylum'].value_counts().index,
                marker = dict(color = 'blue'),
                orientation = 'h'
            ))
            fig_phyl.update_layout(
                title='ITIS TSN by Phylum',
                yaxis = dict(autorange = 'reversed'),
                xaxis_title = 'TSN count',
                plot_bgcolor = '#dbdbdb'
            )
            fig_phyl.update_yaxes(gridcolor = 'white')
            st.plotly_chart(fig_phyl)
            phyl_filter = st.selectbox("Select the Phylum", pd.unique(kingf["phylum"].sort_values()))
        
        with colf2:
            phylf = kingf[kingf['phylum'] == phyl_filter]
            fig_class = go.Figure()
            fig_class.add_trace(go.Bar(
                x = phylf['class'].value_counts(),
                y = phylf['class'].value_counts().index,
                marker = dict(color = 'green'),
                orientation = 'h'
            ))
            fig_class.update_layout(
                title='ITIS TSN by Class',
                yaxis = dict(autorange = 'reversed'),
                xaxis_title = 'TSN count',
                plot_bgcolor = '#dbdbdb'
            )
            fig_class.update_yaxes(gridcolor = 'white')
            st.plotly_chart(fig_class)
            class_filter = st.selectbox("Select the Class", pd.unique(phylf["class"].sort_values())) 

        with colf3:
            classf = phylf[phylf['class'] == class_filter]
            fig_order = go.Figure()
            fig_order.add_trace(go.Bar(
                x = classf['order'].value_counts(),
                y = classf['order'].value_counts().index,
                marker = dict(color = 'orange'),
                orientation = 'h'
            ))
            fig_order.update_layout(
                title='ITIS TSN by Order',
                yaxis = dict(autorange = 'reversed'),
                xaxis_title = 'TSN count',
                plot_bgcolor = '#dbdbdb'
            )
            fig_order.update_yaxes(gridcolor = 'white')
            st.plotly_chart(fig_order)
            order_filter = st.selectbox("Select the Order", pd.unique(classf["order"].sort_values())) 

        with colf4:
            orderf = classf[classf['order'] == order_filter]
            fig_order = go.Figure()
            fig_order.add_trace(go.Bar(
                x = orderf['family'].value_counts(),
                y = orderf['family'].value_counts().index,
                marker = dict(color = 'black'),
                orientation = 'h'
            ))
            fig_order.update_layout(
                title='ITIS TSN by Family',
                yaxis = dict(autorange = 'reversed'),
                xaxis_title = 'TSN count',
                plot_bgcolor = '#dbdbdb'
            )
            fig_order.update_yaxes(gridcolor = 'white')
            st.plotly_chart(fig_order)

st.write('---')

## Search by Common name
# free search box, return sci and vern names sorted by vern name
st.header('Name Search')
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
st.header('Scientific Name Search')
species_search = st.text_input('Species search (e.g. *Ursus* or *Ursus maritimus*)', value = '')
if species_search:
    genus = species_search.split()
    try:
        species_search = species_search.upper()
        search_species = df[df['complete_name'].str.upper() == species_search]
        if not search_species['tsn'].isnull().values.any():
            itis_link = 'https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=' + search_species['tsn'].values[0].astype(str) + ''
            st.write(search_species['name_usage'].values[0] + ' -- ' + itis_link)
            val1 = search_species['tsn'].values[0]
            gdf = gd.to_pandas(filters=(('tsn', '==', val1),))
            sp_dist = gdf[gdf['tsn'] == val1]
            sp_dist_ll = sp_dist.merge(ll, left_on='geographic_value', right_on='geographic_value')
            datamap = px.scatter_geo(sp_dist_ll, lat = 'latitude', lon = 'longitude', color = 'geographic_value')
            datamap.update_traces(marker=dict(size=30))
            st.plotly_chart(datamap)
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
        st.write('please enter a species')

    ## Search by Genus
    #ge_search = st.text_input('Enter Genus (e.g. *Ursus*)', value = '')
    st.markdown('## Genus table')
    ge_search = genus[0]
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
