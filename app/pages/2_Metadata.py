from verden_pa_norsk.streamlit_tools import load_database
from verden_pa_norsk.utils import feltnavn_norsk, feltnavn_ol_norsk
import streamlit as st
from pandas import DataFrame


def get_book_data(mmsid: str) -> tuple[DataFrame, DataFrame]:
    con = load_database("data/translations_map_data.db")
    tr_query = f"SELECT * FROM translations tr WHERE tr.mmsid = '{mmsid}'"
    ol_query = f"SELECT * FROM ol_first_editions ol WHERE ol.mmsid = '{mmsid}'"

    tr_data = con.sql(tr_query).df().transpose()
    ol_data = con.sql(ol_query).df().transpose()
    return tr_data, ol_data


def main():
    st.set_page_config(page_title="Metadata", page_icon="📚", layout="wide")

    if st.query_params:
        mmsid = st.query_params["mmsid"]
    else:
        mmsid = "991418780884702201"

    st.title("Metadata")

    mmsid = st.text_input("Oppgi MMSID", value=mmsid)

    tr_data, ol_data = get_book_data(mmsid)

    tr_data.index = [feltnavn_norsk[x] for x in tr_data.index]
    ol_data.index = [feltnavn_ol_norsk[x] for x in ol_data.index]

    col1, col2 = st.columns(2)

    with col1:
        st.header("Oversettelse (NB)")
        st.dataframe(tr_data, use_container_width=True, height=650)

    with col2:
        st.header("Original (Open Library)")
        st.dataframe(ol_data, use_container_width=True, height=650)

if __name__ == "__main__":
    main()
