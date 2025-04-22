from dhlab import Corpus, Concordance


def build_corpus(author: str, title: str, publication_year: int) -> Corpus:
    """Get corpus

    Args:
        author (str): Author name to search for

    Returns:
        Corpus: dhlab Corpus object contining newspaper mentioning author
    """

    fulltext = f"NEAR({author} {title}, 1000)"

    corpus = Corpus(
        doctype="digavis", from_year=publication_year, to_year=publication_year + 2, fulltext=fulltext, limit=100
    )
    return corpus


def get_concs_for_author(corpus: Corpus, title: str, author: str) -> Concordance:
    """Get concordances for a title and author in a dhlab corpus

    Args:
        corpus (Corpus): target corpus
        title (str): book title
        author (str): author name

    Returns:
        Concordance: author and book collocations
    """
    query = f"{title} AND {author}"  # Contruct query

    colls = Concordance(
        corpus=corpus,
        query=query,
        window=1000,  # Window as high as possible
        limit=10000000,  # Limit as high as possible
    )
    return colls


def get_reviews(author: str, title: str, publication_year: int) -> Concordance:
    """Heuristic to get reviews for a book. Searches concordances for author and title in corpus

    Args:
        author (str): author name
        title (str): book title

    Returns:
        Concordance: resulting concorances. Use style method to render as HTML
    """
    corpus = build_corpus(author, title, publication_year)
    #colls = get_concs_for_author(corpus, title, author)
    return corpus
