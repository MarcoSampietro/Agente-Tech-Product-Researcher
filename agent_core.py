import os
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from tools import get_tools

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "Cronologia"]

# Usiamo Llama-3.3-70b-versatile per il ragionamento superiore
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2) # Temp leggermente più alta per conversazione
tools = get_tools()
llm_with_tools = llm.bind_tools(tools)

# Prompt da Consulente Esperto
SYSTEM_PROMPT = """Sei un Senior Tech Consultant. Il tuo compito è consigliare il prodotto perfetto.

REGOLE DI RAGIONAMENTO:
1. VALUTAZIONE: Prima di cercare, verifica se hai: Budget, Uso principale (gaming, ufficio, editing), e preferenze (es. Windows/Mac).
2. CHIARIMENTO: Se la richiesta è vaga (es. "voglio un pc"), NON USARE TOOL. Rispondi gentilmente chiedendo i dati mancanti.
3. RICERCA: Se hai i dettagli, usa il tool di ricerca per trovare 3 modelli reali con prezzi correnti.
4. SINTESI: Dopo la ricerca, presenta i risultati in una tabella e spiega perché sono adatti all'utente.

IMPORTANTE: Se hai già usato il tool una volta, non usarlo di nuovo. Passa subito alla conclusione."""

def call_model(state: AgentState):
    messages = state['messages']
    
    # Inseriamo il System Prompt
    current_messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    print(f"[AI] Analisi richiesta...")
    response = llm_with_tools.invoke(current_messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    # Se l'AI non ha chiamato tool, significa che sta parlando con l'utente (chiedendo info)
    if not last_message.tool_calls:
        return END
    
    # Se ha chiamato il tool, controlliamo se lo ha già fatto prima
    tool_history = [m for m in messages if isinstance(m, ToolMessage)]
    if len(tool_history) >= 1:
        print("[SISTEMA] Ricerca completata. Generazione sintesi finale.")
        return END
        
    print(f"[TOOL] Ricerca in corso: {last_message.tool_calls[0]['args']}")
    return "action"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", ToolNode(tools))

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"action": "action", END: END})
workflow.add_edge("action", "agent")

graph = workflow.compile()

def run_researcher(messages_history: list):
    """
    Ora accettiamo l'intera cronologia per permettere il botta-e-risposta
    """
    inputs = {"messages": messages_history}
    config = {"recursion_limit": 10}
    try:
        final_state = graph.invoke(inputs, config=config)
        return final_state["messages"][-1].content
    except Exception as e:
        print(f"Errore: {e}")
        return "Mi scuso, ho avuto un problema tecnico. Puoi ripetere i dettagli del PC che cerchi?"
