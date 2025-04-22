import streamlit as st
import requests
import bs4
import pandas as pd
import urllib
from verden_pa_norsk.review_corpus.dhlab_review import get_reviews


def parse_and_unwrap_html(html_snippet):
    """Only look for <em> elements when parsing HTML, discard all others"""
    try:
        soup = bs4.BeautifulSoup(html_snippet, "html.parser")
        for tag in soup.find_all(True):
            if tag.name != 'em':
                tag.unwrap()
            else:
                tag.name = 'strong'
        return str(soup)
    except:
        return ""

def get_nb_search_url(author, title, publication_year):
    query_string = urllib.parse.quote(f"«{author} {title}»~100")
    from_date = str(publication_year) + "0101"
    to_date = str(publication_year + 2) + "1231"
    url = f"https://www.nb.no/search?q={query_string}&mediatype=aviser&fromDate={from_date}&toDate={to_date}"
    return url

def get_reviews_nb(author, title, publication_year):
    query_string = f"«{author} {title}»~100"
    from_date = str(publication_year) + "0101"
    to_date = str(publication_year + 2) + "1231"
    base_url = f"https://api.nb.no/catalog/v1/items?q={query_string}&filter=mediatype:aviser&filter=contentClasses:jp2&filter=date:[{from_date}%20TO%20{to_date}]&aggs=mediatype&aggs=year:9999&aggs=county&snippets=aviser&fragments=2&fragSize=500&size=100&profile=nbdigital"
    r = requests.get(base_url)
    rows = []
    obj = r.json()

    if '_embedded' in obj:
        if 'items' in obj["_embedded"]:
            for item in obj["_embedded"]["items"]:
                urn = item["metadata"]["identifiers"]["urn"]
                title = item["metadata"]["title"]
                timestamp = item["metadata"]["originInfo"]["issued"]
                if "contentFragments" in item:
                    text = item["contentFragments"][0]["text"]
                    text = parse_and_unwrap_html(text)
                    pagenumber = item["contentFragments"][0]["pageNumber"]
                    url = f"https://www.nb.no/items/{urn}?searchText={query_string}&page={pagenumber}"
                    row = [url, title, timestamp, text]
                    rows.append(row)
                else:
                    text = ""
                    url = f"https://www.nb.no/items/{urn}?searchText={query_string}"
                    row = [url, title, timestamp, text]
                    rows.append(row)

    df = pd.DataFrame(rows)
    return df

@st.cache_data
def get_cached_reviews(author, title, publication_year):
    return get_reviews_nb(author, title, publication_year)

def app():
    # Set page configuration
    st.set_page_config(page_title="Omtaler", page_icon="📚", layout="wide")

    st.title("Omtaler")

    # Initialize session state for query params
    if "query_params_initialized" not in st.session_state:
        if st.query_params:
            st.session_state.author = st.query_params["author"]
            st.session_state.title = st.query_params["title"]
            st.session_state.publication_year = int(st.query_params["publication_year"])
        else:
            st.session_state.author = ""
            st.session_state.title = ""
            st.session_state.publication_year = None
        st.session_state.query_params_initialized = True

    # Text input fields
    author = st.text_input("Forfatternavn", value=st.session_state.author)
    title = st.text_input("Boktittel", value=st.session_state.title)
    publication_year = st.number_input("Publikasjonsår", min_value=1400, max_value=2025, value=st.session_state.publication_year)

    # Store inputs in session state
    st.session_state.author = author
    st.session_state.title = title
    st.session_state.publication_year = publication_year

    # Fetch reviews
    if author and title and publication_year:
        res = get_cached_reviews(author, title, publication_year)
        nb_search_url = get_nb_search_url(author, title, publication_year)

        if len(res) > 0:
            res.columns = ["URL", "avistittel", "dato", "treff"]
            res = res.sort_values(by="dato")
            res["dato"] = res["dato"].apply(lambda x: f"{str(x)[6:8]}.{str(x)[4:6]}.{str(x)[:4]}")
            res["URL"] = res["URL"].apply(lambda x: f"<a href='{x}'>URL</a>")

            if len(res) < 100:
                st.write("Fant", str(len(res)), "resultater:")
            else:
                st.markdown(f"Fant mer enn {str(len(res))} resultater. [Gå til Nettbiblioteket for å vise mer.]({nb_search_url}).")

            st.write(res.to_html(escape=False, index=False), unsafe_allow_html=True)

        else:
            st.write("Fant ingen potensielle omtaler.")

if __name__ == "__main__":
    app()
