"""ITIS Taxa Lookup"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import re
import streamlit as st

from datetime import datetime
from fastparquet import ParquetFile



# Streamlit config
st.set_page_config(
    page_title="ITIS Lookup",
    layout="wide",
)
pd.set_option("display.max_rows", None)


def local_css(file_name):
    """CSS format."""
    with open(file_name, encoding="UTF-8") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

def convert_df(data):
    """Convert dataframe to CSV."""
    return data.to_csv().encode("utf-8")

@st.cache_data
def get_data(file) -> pl.DataFrame:
    """Pull data from parquet file."""
    return pl.read_parquet(file)

def color_vald(val):
    """Return green color for valid results."""
    color = "green" if val in {"valid", "accepted"} else "grey"
    return f"background-color: {color}"


def tax_img(tax, frame, col, label):
    """Plot bar charts for each taxon level."""
    title_statement = "ITIS TSN by " + label
    fig = go.Figure()
    counts = frame.get_column(tax).value_counts(sort=True)
    fig.add_trace(
        go.Bar(
            x=counts.get_column("count"),
            y=counts.get_column(tax),
            marker={"color": col},
            orientation="h",
        )
    )
    fig.update_layout(
        title=title_statement,
        yaxis={"autorange": "reversed"},
        xaxis_title="TSN count",
        plot_bgcolor="#dbdbdb",
    )
    fig.update_yaxes(gridcolor="white")
    st.plotly_chart(fig)


local_css("css/streamlit.css")

# Main app
st.header("ITIS Taxa Lookup")
st.write(
    "Data from Integrated Taxonomic Information System (ITIS) - https://www.itis.gov/"
)

st.write("TSN -- Taxonomic Serial Number")
# Get data from parquet file for vernacular names
ITS_VERN = "data/itis_vernacular.parquet"
cn = get_data(ITS_VERN)

if 'cn' not in st.session_state:
    st.session_state.cn = cn

# Get data from parquet file for species data
ITIS_SPEC = "data/itis.parquet"
itis_df = get_data(ITIS_SPEC)

if 'itis_df' not in st.session_state:
    st.session_state.itis_df = itis_df

tsn_count = len(itis_df)
valid = itis_df.filter(pl.col("name_usage") == "valid")
valid_count = len(valid)

# Get data from parquet file for geographics values
GEO = "data/itis_geographic.parquet"
gd = ParquetFile(GEO)
ll = pd.read_csv("data/lat_long.csv")

with st.sidebar:
    st.write("data load date: :blue[20-Feb-2025]")
    st.write("Update 2024-12-10 - :green[Now faster!]")
    st.write("---")
    st.write("Stats:")
    tsn_records = str(tsn_count) + " TSN records"
    st.write(tsn_records)
    valid_records = str(valid_count) + " valid records"
    st.write(valid_records)
    

## Search by Common name
# free search box, return sci and vern names sorted by vern name
st.write(
    ":orange[Note: Scientific name =  complete_name, Common name = vernacular_name]"
)
st.header("Search")
text_search = st.text_input(
    "Find species by name (e.g. polar bear or *Ursus maritimus*):", value=""
)
search_sp = pl.col("complete_name").str.contains(f"(?i){text_search}", strict=True)
search_cn = pl.col("vernacular_name").str.contains(f"(?i){text_search}", strict=True)
df_search = cn.filter(search_sp | search_cn)
df_return = (
    df_search
    .select(["tsn", "complete_name", "vernacular_name"])
    .with_columns([
        pl.col("vernacular_name").str.to_uppercase().alias("vernacular_name_upper"),
        pl.col("tsn").cast(pl.String)
    ])
    .sort("vernacular_name_upper")
    .drop("vernacular_name_upper")
)

if text_search:
    st.dataframe(df_return, use_container_width=True)
    # <--

st.markdown("""---""")

## Search by Species
st.header("Taxonomy Lookup")
species_search = st.text_input(
    "Species search (e.g. *Ursus maritimus*)", value=""
)

## using a regex for \s to define if the search text has multiple words
pattern = r'.*\s.*'
if re.match(pattern, species_search, re.IGNORECASE):
    spp = species_search.split()
    genus = spp[0]
else:
    genus = species_search

## search for a match of the species
try:
    species_search = species_search.upper()
    search_species_df = itis_df.filter(pl.col("complete_name").str.to_uppercase() == species_search)
    search_species = search_species_df.to_pandas()

    ## check if the species exists in the dataframe
    if search_species.empty:
        st.write("Species not found.")
    else:
        ss = search_species[
            [
                "tsn",
                "complete_name",
                "name_usage",
                "unaccept_reason",
                "kingdom",
                "subkingdom",
                "phylum",
                "subphylum",
                "class",
                "superorder",
                "order",
                "suborder",
                "superfamily",
                "family",
                "subfamily",
            ]
        ]

        ## remove the comman from the tsn
        ss[["tsn"]] = ss["tsn"].values[0].astype(str)

        ## map color to the name is valid column
        st.dataframe(ss.set_index(ss.columns[0]).style.map(
                color_vald, subset=["name_usage"]), use_container_width=True)

        # generate the tsn link and the map if the species is found
        if not search_species["tsn"].isnull().values.any():
            itis_link = (
                "https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value="
                + search_species["tsn"].values[0].astype(str)
                + ""
            )
            st.write(search_species["name_usage"].values[0] + " -- " + itis_link)
            val1 = search_species["tsn"].values[0]
            gdf = gd.to_pandas(filters=(("tsn", "==", val1),))
            sp_dist = gdf[gdf["tsn"] == val1]
            if not sp_dist.empty:
                sp_dist_ll = sp_dist.merge(
                    ll, left_on="geographic_value", right_on="geographic_value"
                )
                datamap = px.scatter_geo(
                    sp_dist_ll,
                    lat="latitude",
                    lon="longitude",
                    color="geographic_value",
                )
                datamap.update_traces(marker={"size": 30})
                st.plotly_chart(datamap)
except ValueError:
    st.write("please enter a species")

## Search by Genus to generate a table of genus level matches
st.markdown("## Genus matches")
ge_search = genus.upper()
ge_df = itis_df.filter(pl.col("unit_name1").str.to_uppercase() == ge_search)
ge_df = ge_df[
        [
            "tsn",
            "complete_name",
            "name_usage",
            "unaccept_reason",
            "kingdom",
            "subkingdom",
            "phylum",
            "subphylum",
            "class",
            "superorder",
            "order",
            "suborder",
            "superfamily",
            "family",
            "subfamily",
        ]
    ]

ge_df2 = ge_df.to_pandas()

ge_df2["tsn"] = ge_df2["tsn"].astype(str)
ge_df2 = ge_df2.sort_values(by=["name_usage","complete_name"], ascending=[False,True])
st.dataframe(
    ge_df2.set_index(ge_df2.columns[0]).style.map(
        color_vald, subset=["name_usage"]
    ),
    use_container_width=True,
)

st.markdown("""---""")

current_year = datetime.now().year
CR_STATEMENT = (
    "Copyright (c) "
    + str(current_year)
    + " Conservation Tech Lab at the San Diego Zoo Wildlife Alliance"
)
st.write("Github - https://github.com/ydnadev/itis-data-dash")
st.write(CR_STATEMENT)
