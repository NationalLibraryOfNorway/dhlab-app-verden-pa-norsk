import streamlit as st
import duckdb


@st.cache_resource
def load_database(db_path):
    con = duckdb.connect(db_path, read_only=True)
    return con
