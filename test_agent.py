from agent_graph import graph
from langchain_core.messages import HumanMessage
import dotenv

dotenv.load_dotenv()

def run_test():
    print("--- Tech Researcher Agent (CLI Test) ---")
    user_input = "Quali sono i migliori laptop gaming usciti a fine 2024? Confronta 3 modelli."
    
    config = {"configurable": {"thread_id": "1"}}
    for event in graph.stream(
        {"messages": [HumanMessage(content=user_input)]}, 
        config, 
        stream_mode="values"
    ):
        if "messages" in event:
            last_msg = event["messages"][-1]
            print(f"\n[Node: {last_msg.type}]")
            # Mostra solo il contenuto per brevità
            if last_msg.content:
                print(last_msg.content[:200] + "...")

if __name__ == "__main__":
    run_test()