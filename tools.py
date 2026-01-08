from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool

@tool
def web_search(query: str):
    """
    Cerca sul web prodotti, prezzi e LINK REALI.
    Restituisce i risultati inclusi gli URL delle fonti.
    """
    # Usiamo SearchResults per avere i link strutturati
    search = DuckDuckGoSearchResults()
    return search.run(query)

tools = [web_search]