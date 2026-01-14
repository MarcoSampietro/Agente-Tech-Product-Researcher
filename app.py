import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent_core import run_researcher

st.set_page_config(page_title="AI Tech Advisor", page_icon="💻")

st.title("🔍 Tech Product Advisor")
st.caption("Consulente hardware esperto con accesso al mercato real-time")

# Inizializza memoria in session_state se non esiste
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Visualizza i messaggi precedenti
for message in st.session_state.chat_history:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# Input utente
if prompt := st.chat_input("Di che tipo di hardware hai bisogno?"):
    # Aggiungi messaggio utente alla storia
    user_msg = HumanMessage(content=prompt)
    st.session_state.chat_history.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ragionando..."):
            # Passiamo l'intera cronologia all'agente
            response_text = run_researcher(st.session_state.chat_history)
            
            st.markdown(response_text)
            # Aggiungi risposta AI alla storia
            st.session_state.chat_history.append(AIMessage(content=response_text))
