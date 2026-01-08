import streamlit as st
import json, re, os
from langchain_core.messages import HumanMessage, AIMessage
from agent_graph import get_agent_graph

st.set_page_config(page_title="Tech Researcher AI", layout="wide")

# CSS per rendere la tabella bella
st.markdown("""
    <style>
    .tech-table { width:100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; color: white; }
    .tech-table th { background-color: #262730; color: #4497ff; padding: 12px; text-align: left; border: 1px solid #444; }
    .tech-table td { padding: 10px; border: 1px solid #444; vertical-align: top; }
    .price-orig { text-decoration: line-through; color: #ff4b4b; font-size: 12px; }
    .price-now { color: #28a745; font-weight: bold; font-size: 16px; display: block; }
    .specs { font-size: 12px; line-height: 1.4; }
    .buy-btn { background-color: #007bff; color: white !important; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def render_html_table(products):
    if not products: return ""
    
    rows = ""
    for p in products:
        # Gestione Prezzo
        p_orig = p.get('prezzo_originale', 'N/A')
        p_scont = p.get('prezzo_scontato')
        if p_scont and p_scont != p_orig:
            prezzo_td = f'<span class="price-orig">{p_orig}</span><span class="price-now">{p_scont}</span>'
        else:
            prezzo_td = f'<span class="price-now">{p_orig}</span>'
        
        # Gestione Specs
        specs_td = f"""<div class="specs">
            <b>CPU:</b> {p.get('cpu','-')}<br>
            <b>RAM:</b> {p.get('ram','-')}<br>
            <b>SSD:</b> {p.get('ssd','-')}<br>
            <b>GPU:</b> {p.get('gpu','-')}
        </div>"""
        
        # Gestione Link
        link_url = p.get('link', '#')
        link_td = f'<a href="{link_url}" target="_blank" class="buy-btn">Vedi Offerta</a>'
        
        rows += f"""
        <tr>
            <td><b>{p.get('nome','-')}</b></td>
            <td>{prezzo_td}</td>
            <td>{specs_td}</td>
            <td>{p.get('commento','-')}</td>
            <td>{link_td}</td>
        </tr>
        """
    
    return f"""
    <table class="tech-table">
        <thead>
            <tr>
                <th>Prodotto</th>
                <th>Prezzo</th>
                <th>Caratteristiche</th>
                <th>Recensione AI</th>
                <th>Azione</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """

st.title("🚀 Tech Researcher AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra Chat
for msg in st.session_state.messages:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content, unsafe_allow_html=True)

# Input
if prompt := st.chat_input("Esempio: Trova 3 laptop gaming sotto i 1200 euro"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Ricerca in corso..."):
                graph = get_agent_graph()
                result = graph.invoke({"messages": st.session_state.messages, "iteration": 0})
                
                full_response = result["messages"][-1].content
                
                # Estrazione dati
                data_match = re.search(r"<data>(.*?)</data>", full_response, re.DOTALL)
                
                clean_text = full_response
                table_html = ""
                
                if data_match:
                    try:
                        products = json.loads(data_match.group(1).strip())
                        table_html = render_html_table(products)
                        clean_text = full_response.replace(data_match.group(0), "")
                    except:
                        st.error("Errore nel parsing dei dati del prodotto.")

                # Visualizzazione finale
                st.markdown(clean_text)
                if table_html:
                    st.markdown(table_html, unsafe_allow_html=True)
                
                st.session_state.messages.append(AIMessage(content=clean_text + table_html))
                
        except Exception as e:
            st.error(f"Errore: {e}")