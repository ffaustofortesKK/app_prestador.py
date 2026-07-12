import streamlit as st
import qrcode
from io import BytesIO
from supabase import create_client
import requests
from bs4 import BeautifulSoup

# Configuração
url = st.secrets["URL_SUPABASE"]
key = st.secrets["KEY_SUPABASE"]
supabase = create_client(url, key)

st.set_page_config(page_title="Painel do Prestador", layout="centered")

# --- ESTILO DARK MODE ---
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; }
    h1, h2, h3, p, label, div { color: #ffffff !important; }
    .big-box { background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    .sintonia-box { background-color: #260000; padding: 15px; border-radius: 5px; border: 1px solid #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

# Função de busca simulada (Ajuste o seletor CSS se necessário)
def buscar_musicas(termo):
    url_base = "https://www.nephobox.com/portuguese/main?category=all&path=%2FKARAOKE"
    try:
        response = requests.get(url_base)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Buscando elementos que contenham nomes de arquivos
        links = soup.find_all('a')
        resultados = [link.text for link in links if termo.lower() in link.text.lower()]
        return resultados[:10] if resultados else ["Nenhuma música encontrada com este termo."]
    except Exception as e:
        return [f"Erro na conexão: {e}"]

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
    
    slug = st.session_state["slug"]
    url_cliente = f"https://ffkaraoke-cliente.streamlit.app/?prestador={slug}"
    st.info(f"Link do cliente: {url_cliente}")

    # Interface de Busca e Adição
    st.markdown('<div class="big-box">', unsafe_allow_html=True)
    st.subheader("🔍 Pesquisar na Nuvem")
    termo = st.text_input("Digite o nome da música:")
    
    if st.button("Buscar"):
        st.session_state["resultados"] = buscar_musicas(termo)
    
    if "resultados" in st.session_state:
        selecionada = st.selectbox("Selecione a música:", st.session_state["resultados"])
        if st.button("Adicionar à Lista"):
            st.success(f"Adicionado: {selecionada}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Fila e Sistema Cloud
    st.markdown("### Fila de Reprodução")
    if st.button("Sair"):
        st.session_state["prestador_id"] = None
        st.rerun()
