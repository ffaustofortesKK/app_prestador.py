import streamlit as st
import requests
from supabase import create_client

# Configurações
url = st.secrets["URL_SUPABASE"]
key = st.secrets["KEY_SUPABASE"]
supabase = create_client(url, key)

# URL da Fila no Firebase
def get_url_fila(slug):
    return f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

st.set_page_config(page_title="Gestão de Karaoke", layout="wide")

# ... (Mantenha aqui a sua lógica de Login e Setup de sessão) ...

if st.session_state.prestador_id:
    st.title("📋 Gestão de Fila")
    slug = st.session_state.slug
    url_fila = get_url_fila(slug)

    # 1. BUSCAR PEDIDOS
    resp = requests.get(url_fila).json() or {}
    pedidos = list(resp.items()) # Lista de (id, dados)

    # 2. INTERFACE DA FILA
    for i, (p_id, p) in enumerate(pedidos):
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 2])
        col1.write(f"{i+1}. **{p.get('cantor')}**: {p.get('musica')}")
        
        # Botões de Controle
        if col2.button("⬆️", key=f"up_{p_id}"):
            # Lógica para trocar a ordem no Firebase (requer manipulação de lista)
            pass 
        if col3.button("🗑️", key=f"del_{p_id}"):
            requests.delete(f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}/{p_id}.json")
            st.rerun()
            
        if col5.button("🎤 Anunciar e Iniciar", key=f"start_{p_id}"):
            # Envia sinal para a TELA DE APRESENTAÇÃO iniciar contagem
            requests.patch(f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json", 
                           json={"acao": "contagem", "cantor": p.get('cantor')})
            st.success("Contagem iniciada na TV!")

    if st.button("🔄 Atualizar Fila"):
        st.rerun()
