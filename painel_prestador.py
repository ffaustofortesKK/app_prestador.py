import streamlit as st
import qrcode
from io import BytesIO
from supabase import create_client

# Configuração
url = st.secrets["URL_SUPABASE"]
key = st.secrets["KEY_SUPABASE"]
supabase = create_client(url, key)

st.set_page_config(page_title="Painel do Prestador", layout="centered")

if "prestador_id" not in st.session_state:
    st.session_state["prestador_id"] = None

# --- LOGIN ---
if st.session_state["prestador_id"] is None:
    st.title("🎤 Portal do Prestador")
    nome = st.text_input("Nome de Usuário:")
    senha = st.text_input("Senha:", type="password")
    
    if st.button("Entrar"):
        res = supabase.table("prestadores").select("*").eq("nome_prestador", nome).eq("senha_acesso", senha).execute()
        if res.data:
            st.session_state["prestador_id"] = res.data[0]["id"]
            st.session_state["nome"] = res.data[0]["nome_prestador"]
            st.session_state["slug"] = res.data[0]["slug_unico"]
            st.rerun()
        else:
            st.error("Credenciais inválidas!")

# --- PAINEL ---
else:
    st.title(f"🎤 Bem-vindo, {st.session_state['nome']}!")
    
    # Link e QR Code
    slug = st.session_state["slug"]
    url_cliente = f"https://ffkaraoke-cliente.streamlit.app/?prestador={slug}"
    st.info(f"Link do cliente: {url_cliente}")
    
    # Interface de Pedidos
    with st.expander("➕ Adicionar Música", expanded=True):
        nome_cantor = st.text_input("Nome do Cantor:")
        musica = st.text_input("Nome da Música:")
        if st.button("Adicionar"):
            st.success("Adicionado!")

    # Fila (Renomeado para evitar o erro de ancoragem do link)
    st.markdown("### Fila de Reprodução")
    
    col1, col2, col3 = st.columns(3)
    col1.button("Subir")
    col2.button("Descer")
    col3.button("Remover")

    # Sistema Cloud
    st.warning("### SISTEMA EM SINTONIA CLOUD")
    c1, c2 = st.columns(2)
    c1.button("Validar")
    c2.button("Recusar")

    if st.button("Sair"):
        st.session_state["prestador_id"] = None
        st.rerun()
