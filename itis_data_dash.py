"""ITIS Taxa Lookup"""

from datetime import datetime
from fastparquet import ParquetFile

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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


local_css("css/streamlit.css")


def convert_df(data):
    """Convert dataframe to CSV."""
    return data.to_csv().encode("utf-8")


def get_data(file) -> pd.DataFrame:
    """Pull data from parquet file."""
    return pd.read_parquet(file)


def color_vald(val):
    """Return green color for valid results."""
    color = "green" if val in {"valid", "accepted"} else ""
    return f"background-color: {color}"


def tax_img(tax, frame, col, label):
    """Plot bar charts for each taxon level."""
    title_statement = "ITIS TSN by " + label
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=frame[tax].value_counts(),
            y=frame[tax].value_counts().index,
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


# Main app
st.header("ITIS Taxa Lookup")
st.write(
    "Data from Integrated Taxonomic Information System (ITIS) - https://www.itis.gov/"
)
st.write("data load date: :blue[19-Nov-2024]")
st.write("TSN -- Taxonomic Serial Number")

# Get data from parquet file for vernacular names
ITS_VERN = "data/itis_vernacular.parquet"
cn = get_data(ITS_VERN)

# Get data from parquet file for species data
ITIS_SPEC = "data/itis.parquet"
df = get_data(ITIS_SPEC)

# Get data from parquet file for geographics values
GEO = "data/itis_geographic.parquet"
gd = ParquetFile(GEO)
ll = pd.read_csv("data/lat_long.csv")

# Summation charts
with st.expander("Groupings by Taxa"):
    c1, c2, c3 = st.columns(3)
    with c2:
        tax_img("kingdom", df, "crimson", "Kingdom")

    king_filter = st.selectbox(
        "Select the Kingdom", pd.unique(df["kingdom"].sort_values())
    )

    if king_filter:
        kingf = df[df["kingdom"] == king_filter]

        colf1, colf2 = st.columns(2)
        colf3, colf4 = st.columns(2)

        with colf1:
            tax_img("phylum", kingf, "blue", "Phylum")
            phyl_filter = st.selectbox(
                "Select the Phylum", pd.unique(kingf["phylum"].sort_values())
            )

        with colf2:
            phylf = kingf[kingf["phylum"] == phyl_filter]
            tax_img("class", phylf, "green", "Class")
            class_filter = st.selectbox(
                "Select the Class", pd.unique(phylf["class"].sort_values())
            )

        with colf3:
            classf = phylf[phylf["class"] == class_filter]
            tax_img("order", classf, "orange", "Order")
            order_filter = st.selectbox(
                "Select the Order", pd.unique(classf["order"].sort_values())
            )

        with colf4:
            orderf = classf[classf["order"] == order_filter]
            tax_img("family", orderf, "black", "Family")
            # fig_order = go.Figure()
            # fig_order.add_trace(
            #    go.Bar(
            #        x=orderf["family"].value_counts(),
            #        y=orderf["family"].value_counts().index,
            #        marker={"color":"black"},
            #        orientation="h",
            #    )
            # )
            # fig_order.update_layout(
            #    title="ITIS TSN by Family",
            #    yaxis={"autorange":"reversed"},
            #    xaxis_title="TSN count",
            #    plot_bgcolor="#dbdbdb",
            # )
            # fig_order.update_yaxes(gridcolor="white")
            # st.plotly_chart(fig_order)

## Search by Common name
# free search box, return sci and vern names sorted by vern name
st.write(
    ":orange[Note: Scientific name =  complete_name, Common name = vernacular_name]"
)
st.header("Name Search")
text_search = st.text_input(
    "Find species by name (e.g. polar bear or *Ursus maritimus*):", value=""
)
search_sp = cn["complete_name"].str.contains(text_search, case=False)
search_cn = cn["vernacular_name"].str.contains(text_search, case=False)
df_search = cn[search_sp | search_cn]
df_return = df_search[["tsn", "complete_name", "vernacular_name"]]
df_return["vernacular_name_upper"] = df_return["vernacular_name"].str.upper()
df_return = df_return.sort_values(by=["vernacular_name_upper"])
df_return["tsn"] = df_return["tsn"].astype(str)
del df_return["vernacular_name_upper"]
if text_search:
    st.dataframe(df_return.set_index(df_return.columns[0]), use_container_width=True)
    # <--

st.markdown("""---""")

## Search by Species
st.header("Scientific Name Search")
species_search = st.text_input(
    "Species search (e.g. *Ursus maritimus*)", value=""
)
if species_search:
    genus = species_search.split()
    try:
        species_search = species_search.upper()
        search_species = df[df["complete_name"].str.upper() == species_search]
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
        if not search_species["kingdom"].isnull().values.any():
            st.write("KINGDOM - " + search_species["kingdom"].values[0])
        if not search_species["subkingdom"].isnull().values.any():
            st.write("SUBKINGDOM - " + search_species["subkingdom"].values[0])
        if not search_species["phylum"].isnull().values.any():
            st.write("----- PHYLUM - " + search_species["phylum"].values[0])
        if not search_species["subphylum"].isnull().values.any():
            st.write("----- SUBPHYLUM - " + search_species["subphylum"].values[0])
        if not search_species["class"].isnull().values.any():
            st.write("----- ----- CLASS - " + search_species["class"].values[0])
        if not search_species["superorder"].isnull().values.any():
            st.write(
                "----- ----- ----- SUPERORDER - "
                + search_species["superorder"].values[0]
            )
        if not search_species["order"].isnull().values.any():
            st.write("----- ----- ----- ORDER - " + search_species["order"].values[0])
        if not search_species["suborder"].isnull().values.any():
            st.write(
                "----- ----- ----- SUBORDER - " + search_species["suborder"].values[0]
            )
        if not search_species["superfamily"].isnull().values.any():
            st.write(
                "----- ----- ----- ----- SUPERFAMILY - "
                + search_species["superfamily"].values[0]
            )
        if not search_species["family"].isnull().values.any():
            st.write(
                "----- ----- ----- ----- FAMILY - " + search_species["family"].values[0]
            )
        if not search_species["subfamily"].isnull().values.any():
            st.write(
                "----- ----- ----- ----- SUBFAMILY - "
                + search_species["subfamily"].values[0]
            )
    except ValueError:
        st.write("please enter a species")

    ## Search by Genus
    st.markdown("## Genus table")
    ge_search = genus[0]
    ge_search = ge_search.title()
    placeholder = st.empty()
    search_ge = df[df["unit_name1"] == ge_search]
    df2 = search_ge.sort_values(by=["complete_name"])

    ## Dataframe based on Genus
    df1 = df2[
        [
            "tsn",
            "name_usage",
            "complete_name",
            "subfamily",
            "family",
            "superfamily",
            "suborder",
            "order",
            "superorder",
            "class",
            "subphylum",
            "phylum",
            "subkingdom",
            "kingdom",
        ]
    ]

    if ge_search:
        df1["tsn"] = df1["tsn"].astype(str)
        st.dataframe(
            df1.set_index(df1.columns[0]).style.applymap(
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
