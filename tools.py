import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

def get_tools():
    # Riduciamo max_results a 3 e togliamo raw_content per risparmiare token
    search_tool = TavilySearchResults(
        max_results=3,
        search_depth="basic", # "basic" è più veloce e consuma meno
        include_answer=True,
        include_raw_content=False 
    )
    return [search_tool]

if __name__ == "__main__":
    tool_list = get_tools()
    search = tool_list[0]
    print("Test ricerca light...")
    results = search.invoke({"query": "miglior laptop studenti 500 euro 2024"})
    print(f"Token salvati! Risultati ottenuti: {len(results)}")
