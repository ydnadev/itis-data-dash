""" ITIS Taxonomy groupings """

import plotly.graph_objects as go
import polars as pl
import streamlit as st


#def color_vald(val):
#    """Return green color for valid results."""
#    color = "green" if val in {"valid", "accepted"} else "grey"
#    return f"background-color: {color}"

#def get_data(file) -> pl.DataFrame:
#    """Pull data from parquet file."""
#    return pl.read_parquet(file)


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


# Get data from parquet file for species data
#ITIS_SPEC = "data/itis.parquet"
#df = get_data(ITIS_SPEC)

if 'itis_df' in st.session_state:
    itis_df = st.session_state.itis_df
else:
    st.write("ITIS dataframe not loaded")

c1, c2, c3 = st.columns(3)
with c2:
    tax_img("kingdom", itis_df, "crimson", "Kingdom")

king_filter = st.selectbox(
    "Select the Kingdom", itis_df.get_column("kingdom").unique().sort()
)

if king_filter:

    kingf = itis_df.filter(pl.col("kingdom") == king_filter)

    colf1, colf2 = st.columns(2)
    colf3, colf4 = st.columns(2)
    colf5, colf6 = st.columns(2)

    with colf1:
        tax_img("phylum", kingf, "blue", "Phylum")
        phyl_filter = st.selectbox(
            "Select the Phylum", kingf.get_column("phylum").unique().sort()
        )

    with colf2:
        phylf = kingf.filter(pl.col("phylum") == phyl_filter)
        tax_img("class", phylf, "green", "Class")
        class_filter = st.selectbox(
            "Select the Class", phylf.get_column("class").unique().sort()
        )

    with colf3:
        classf = phylf.filter(pl.col("class") == class_filter)
        tax_img("order", classf, "orange", "Order")
        order_filter = st.selectbox(
            "Select the Order", classf.get_column("order").unique().sort()
        )

    with colf4:
        orderf = classf.filter(pl.col("order") == order_filter)
        tax_img("family", orderf, "black", "Family")
        family_filter = st.selectbox(
            "Select the Family", orderf.get_column("family").unique().sort()
        )

    with colf6:
        famf = orderf.filter(pl.col("family") == family_filter)
        family_data = famf[
            [
                "tsn",
                "complete_name",
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

        family_data = family_data.with_columns(pl.col("tsn").cast(str))
        family_df = family_data.to_pandas()

        st.dataframe(
            family_df,
            use_container_width=True,
        )
