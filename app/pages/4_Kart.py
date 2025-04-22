import pandas as pd
import folium
from folium.plugins import Fullscreen, FastMarkerCluster, MarkerCluster
import duckdb
import streamlit as st
from streamlit_folium import st_folium

# Constants
DDB_CONNECTION = "data/translations_map_data.db"

@st.cache_data
def query_builder(address="", publication_year=(1800,2024), author="", translator=""):
    params = []

    if address:
        address_cond = "address = ?"
        params.append(address)
    else:
        address_cond = "address IS NOT NULL"

    params.extend([publication_year[0], publication_year[1]])

    where_clause = f"""WHERE ({address_cond}) AND (tr.ddc800 IS TRUE OR tr.ddc0 IS TRUE)
            AND (tr.publication_year_int BETWEEN ? AND ?)"""
    
    if author:
        author = f"%{author}%"
        where_clause += " AND (tr.main_author ILIKE ?)"
        params.append(author)

    if translator:
        translator = f"%{translator}%"
        where_clause += " AND (tr.translators::varchar ILIKE ?)"
        params.append(translator)

    return where_clause, params

@st.cache_data
def load_city_data(where_clause, params) -> pd.DataFrame:
    ddb = duckdb.connect(DDB_CONNECTION, read_only=True)

    city_count_data = ddb.sql(
        f"""SELECT ol.address,
                ol.latitude,
                ol.longitude,
                COUNT(ol.mmsid) AS books_published
            FROM ol_first_editions ol
            JOIN translations tr ON ol.mmsid = tr.mmsid
            {where_clause}
            GROUP BY address,
                    latitude,
                    longitude
                ORDER BY books_published DESC
        """,
    params=params).df()

    # city_count_data = ddb.execute("SELECT * FROM city_count").df()
    return city_count_data


@st.cache_resource
def create_map(where_clause, params) -> folium.Map:
    data = load_city_data(where_clause, params)

    folium_map = folium.Map(location=[10, 150], zoom_start=2)

    marker_cluster = MarkerCluster(
        name='Clustered books',
        overlay=True,
        control=False,
        icon_create_function=None
    )

    # Add points to the map with CircleMarker
    for idx, row in data.iterrows():
        marker = folium.Marker(location=[row["latitude"], row["longitude"]], tooltip=row["address"])
        marker_cluster.add_child(marker)

    marker_cluster.add_to(folium_map)
    fullscreen = Fullscreen()
    fullscreen.add_to(folium_map)

    return folium_map


def get_address_books(where_clause, params) -> pd.DataFrame:
    ddb = duckdb.connect(DDB_CONNECTION, read_only=True)
    query = f"""SELECT ol.mmsid,
                        ol.title as originaltittel,
                        tr.title as tittel,
                        tr.subtitle as undertittel,
                        tr.contributors as bidragsytere,
                        ol.author as forfatter,
                        CAST(ol.publish_year as VARCHAR) as publikasjonsår,
                        ol.publishers as forlag,
                        ol.publish_places_all as publikasjonssteder_alle,
                        ol.publish_places publikasjonssteder,
                        ol.address as adresse,
                        ol.work_key as verksnøkkel,
                FROM ol_first_editions ol
                JOIN translations tr ON ol.mmsid = tr.mmsid
                {where_clause}
            """

    books_data = ddb.sql(query, params=params).df()
    books_data["mmsid"] = books_data["mmsid"].apply(
        lambda x: f"Metadata?mmsid={x}"
    )
    books_data["verksnøkkel"] = books_data["verksnøkkel"].apply(
        lambda x: f"https://www.openlibrary.org{x}"
    )
    return books_data


@st.cache_resource
def connect_to_ddb():
    return duckdb.connect(DDB_CONNECTION, read_only=True)

def main():
    st.set_page_config(page_title="Kart", page_icon="📚", layout="wide")
    st.title("Kart over oversatte bøker")

    publication_year = st.slider("Publikasjonsår", min_value=1800, max_value=2024, value=(1800, 2024))
    col1, col2 = st.columns(2)

    with col1:
        author = st.text_input("Forfatter")
    with col2:
        translator = st.text_input("Oversetter")

    where_clause, params = query_builder(publication_year=publication_year, author=author, translator=translator)

    map = create_map(where_clause, params)

    output = st_folium(
        map, width=2000, height=600, returned_objects=["last_object_clicked_tooltip"]
    )
    # folium_static(map)

    address = output["last_object_clicked_tooltip"]

    if address:
        where_clause, params = query_builder(address=address, publication_year=publication_year, author=author, translator=translator)
        df = get_address_books(where_clause, params)
        col_order = ['mmsid', 'forfatter', 'tittel', 'originaltittel', 'publikasjonsår', 'publikasjonssteder_alle', 'publikasjonssteder', 'forlag' ,'bidragsytere', 'undertittel', 'adresse', 'verksnøkkel']

        df = df[col_order]

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "mmsid": st.column_config.LinkColumn("#", display_text="📚"),
                "verksnøkkel": st.column_config.LinkColumn("verksnøkkel"),
            },
        )

if __name__ == "__main__":
    main()
