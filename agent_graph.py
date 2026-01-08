import os
from typing import Annotated, TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, AIMessage
import dotenv

dotenv.load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    iteration: int
    finished: bool

def get_agent_graph():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    from tools import tools
    llm_with_tools = llm.bind_tools(tools)

    def reasoning_node(state: AgentState):
        it = state.get("iteration", 0)
        if it > 5: return {"finished": True}

        system_prompt = SystemMessage(content=(
            "Sei un Tech Researcher. REGOLE PER I DATI:\n"
            "1. Trova prodotti reali e i loro URL di acquisto o recensione nei risultati di ricerca.\n"
            "2. Estrai il link esatto (es. https://amazon.it/... o https://mediaworld.it/...).\n"
            "3. NON INVENTARE LINK. Se non trovi un link diretto, usa l'URL della fonte della ricerca.\n"
            "4. Genera SEMPRE il blocco JSON tra <data> e </data> con queste chiavi:\n"
            "nome, prezzo_originale, prezzo_scontato, cpu, ram, ssd, gpu, commento, link."
        ))

        response = llm_with_tools.invoke([system_prompt] + state["messages"])
        is_finished = "<data>" in response.content if response.content else False
        return {"messages": [response], "iteration": it + 1, "finished": is_finished}

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", reasoning_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("agent")
    
    def should_continue(state: AgentState):
        if state.get("finished") or not state["messages"][-1].tool_calls:
            return END
        return "tools"

    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    return workflow.compile()