import streamlit as st

DOC_PATH = "resources/markdown/Document.md"


def get_file(file_path, method="r"):
    with open(file_path, "r") as file:
        data = file.read()
    return data


def main():
    st.set_page_config(
        page_title="Verden på norsk",
        page_icon="📚",
        layout="wide",
    )

    md = get_file("resources/markdown/Document.md")
    st.markdown(md, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
