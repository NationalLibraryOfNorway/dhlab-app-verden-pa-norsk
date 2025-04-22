import streamlit as st
import duckdb
import pandas as pd
from pandas import DataFrame, Series
from verden_pa_norsk.utils import feltnavn_norsk

db_path = "data/translations_map_data.db"
table_name = "translations"

@st.cache_data
def get_column_names_and_types(table_name):
    with duckdb.connect(db_path, read_only=True) as con:
        query = f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        """
        return [(row[0], row[1]) for row in con.execute(query).fetchall()]

@st.cache_data
def get_available_languages():
    with duckdb.connect(db_path, read_only=True) as con:
        query = """
        SELECT DISTINCT l."language_code", l."language_nob" as language 
        FROM translations t 
        JOIN languages l ON l.language_code = t.original_language
        ORDER BY l."language_nob";
        """
        return [(row[0], row[1]) for row in con.execute(query).fetchall()]

def split(a, n):
    "Split list a into n parts"
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))

def switch_author_name(author: str | None) -> str | None:
    if author is None:
        return None
    else:
        return " ".join(author.split(", ")[::-1])

def remove_subtitle(title: str | None) -> str | None:
    return title.split(":")[0].strip()

def sub_space_and_punct(text: str) -> str:
    return text.replace(".", "").replace(" ", "%20")

def generate_dhlab_review_link(author: str, title: str, publication_year_int: int) -> str:
    link = f"Omtaler?author={sub_space_and_punct(author)}&title={sub_space_and_punct(title)}&publication_year={publication_year_int}"
    return link

def get_dhlab_review_links(df: DataFrame) -> Series:
    authors = df["main_author"].apply(switch_author_name)
    titles = df["title"].apply(remove_subtitle)
    publication_year_int = df["publication_year_int"]

    target = pd.concat([authors, titles, publication_year_int], axis=1).dropna()

    return target.apply(
        lambda x: generate_dhlab_review_link(x["main_author"], x["title"], x["publication_year_int"]), axis=1
    )

@st.cache_data(show_spinner = False)
def run_query(user_inputs):
    with duckdb.connect(db_path, read_only=True) as con:
        if len(user_inputs) == 0:
            query = f"SELECT t.*, ol.publish_year, u.urn FROM {table_name} t LEFT JOIN urn_mmsid u ON u.mmsid = t.mmsid LEFT JOIN ol_first_editions ol ON ol.mmsid = t.mmsid"
        else:
            params = []
            where_clauses = []
            
            for col in user_inputs:
                _type = user_inputs[col]['type']
                _input = user_inputs[col]['input']

                if isinstance(_input, list) == False and isinstance(_input, tuple) == False:
                    _input = [_input]
                
                if col == 'ddc800' and _input == [True]:
                    where_clause = '(ddc800 is true or ddc0 is true)'
                elif col == "contributors" or col == "translators":
                    where_clause =  '(' + ' OR '.join([f"{col}::varchar ILIKE ?" for x in _input]) + ')'
                    _input = [f'%{x}%' for x in _input]
                    params.extend(_input)
                elif col == "publication_year_int":
                    where_clause =  f"({col} BETWEEN ? AND ?)"
                    params.extend(list(_input))
                elif col == "language":
                    if isinstance(_input[0], list):
                        where_clause = f"{col} IN (?, ?, ?)"
                        params.extend(_input[0])
                    else:
                        where_clause = f"{col} == ?"
                        params.extend(_input)
                else:
                    where_clause =  '(' + ' OR '.join([f"{col} ILIKE ?" for x in _input]) + ')'
                    _input = [f'%{x}%' for x in _input]
                    params.extend(_input)
            
                where_clauses.append(where_clause)
            
            where_statement = " AND ".join(where_clauses)
            query = f"SELECT t.*, ol.publish_year, u.urn FROM {table_name} t LEFT JOIN urn_mmsid u ON u.mmsid = t.mmsid LEFT JOIN ol_first_editions ol ON ol.mmsid = t.mmsid WHERE {where_statement}"

        res = con.execute(query, params).df()
        return res

def main():
    st.set_page_config(
        page_title="Verden på norsk",
        page_icon="📚",
        layout="wide",
    )

    # st.page_config(layout="wide")
    st.title("Boksøk")
    
    # Get column names
    columns = get_column_names_and_types(table_name)

    # get avilable languages in the corpus
    target_languages = {'Begge målformer': ['nor', 'nob', 'nno'], 'Bokmål': 'nob', 'Nynorsk': 'nno'}
    languages = get_available_languages()
    languages = {x[1]: x[0] for x in languages}

    with st.form(key='corpus_form'):
        # Create input fields for each column
        user_inputs = {}
        stcols = st.columns(3)
        column_lists = split(columns, 3)
        for column_list, stcol in zip(column_lists, stcols):
            with stcol:
                for col in column_list:
                    column_name = col[0]
                    column_type = col[1]

                    # skip certain fields
                    if column_name in ('mmsid', 'ddc', 'publication_year_str', 'ddc0', 'contributors', 'subtitle'):
                        continue
                    if column_name == "ddc800":
                        user_input = st.checkbox("Begrens til oversatte bøker i Dewey 800-serien (skjønnlitteratur) og bøker uten Dewey-kode", key=column_name, value=True)
                    elif column_name == "publication_year_int":
                        user_input = st.slider(f"{feltnavn_norsk[column_name]}", min_value=1800, max_value=2024, value=(1800, 2024), key=column_name)
                    elif column_name == "language":
                        user_input = st.multiselect(f"{feltnavn_norsk[column_name]}", target_languages.keys(), key=column_name, placeholder="Velg én eller flere målformer")
                        if user_input:
                            user_input = [target_languages[x] for x in user_input]
                    elif column_name == "original_language":
                        user_input = st.multiselect(f"{feltnavn_norsk[column_name]}", languages.keys(), key=column_name, placeholder="Velg ett eller flere språk")
                        if user_input:
                            user_input = [languages[x] for x in user_input]
                    else:
                        user_input = st.text_input(f"{feltnavn_norsk[column_name]}", key=column_name)
                    
                    if user_input:
                        user_inputs[column_name] = {'input' :user_input, 'type' :column_type}

        submitted = st.form_submit_button("Søk")

    if submitted:
        res = run_query(user_inputs)
        if len(res) > 0:
            # apply mapping
            try:
                res["links"] = get_dhlab_review_links(res)
            except:
                res["links"] = ""

            res.urn = res.urn.apply(lambda x: f"https://urn.nb.no/{x}" if x else None)

            res.columns = [feltnavn_norsk[x].lower() for x in res.columns]

            res["mmsid"] = res["mmsid"].apply(lambda x: f"Metadata?mmsid={x}")

            col_order = ['urn', 'forfatter', 'oversetter', 'oversatt tittel', 'publikasjonsår oversettelse', 'målform', 'norsk forlag', 'originaltittel', "originalspråk", "publikasjonsår originaltittel", 'ddc800', 'ddc0', 'lenker', 'mmsid']

            res = res[col_order]

            # sort by year
            res = res.sort_values(by="publikasjonsår oversettelse")

            st.write(f"Antall treff: {len(res)}")
            st.dataframe(
                res,
                hide_index=True,
                use_container_width=True,
                column_config={"urn": st.column_config.LinkColumn("urn", display_text="📖"), "lenker": st.column_config.LinkColumn("omtale", display_text="🔍"),
                "mmsid": st.column_config.LinkColumn("metadata", display_text="📚"), "publikasjonsår oversettelse": st.column_config.NumberColumn(format="%d"), "publikasjonsår originaltittel": st.column_config.NumberColumn(format="%d")},
            )

if __name__ == "__main__":
    main()
