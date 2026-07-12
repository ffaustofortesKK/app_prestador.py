import streamlit as st
import qrcode
from io import BytesIO
from supabase import create_client
import requests
from bs4 import BeautifulSoup

# Configuração do Supabase
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
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE BUSCA NA NUVEM ---
def buscar_musicas(termo):
    headers = {"User-Agent": "Mozilla/5.0"}
    url_base = "https://www.nephobox.com/portuguese/main?category=all&path=%2FKARAOKE"
    try:
        response = requests.get(url_base, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        resultados = [item.text.strip() for item in soup.find_all(['a', 'div', 'span']) if termo.lower() in item.text.lower()]
        return list(set(resultados[:10])) if resultados else ["Nenhuma música encontrada."]
    except Exception as e:
        return [f"Erro: {e}"]

# Inicializar sessão
if "prestador_id" not in st.session_state:
    st.session_state["prestador_id"] = None

# --- FLUXO PRINCIPAL ---
if st.session_state["prestador_id"] is None:
    # TELA DE LOGIN
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

else:
    # TELA DO PAINEL (LOGADO)
    st.title(f"🎤 Bem-vindo, {st.session_state['nome']}!")
    
    # Gerar Link do Cliente
    slug = st.session_state["slug"]
    url_cliente = f"https://ffkaraoke-cliente.streamlit.app/?prestador={slug}"
    st.info(f"Link do cliente: {url_cliente}")

    # Gerar QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url_cliente)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="#0e0e0e")
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.write("### Escaneie para pedir músicas:")
    st.image(buf.getvalue(), width=200)

    # Interface de Busca
    st.markdown('<div class="big-box">', unsafe_allow_html=True)
    st.subheader("🔍 Pesquisar na Nuvem")
    termo = st.text_input("Nome da Música:")
    
    if st.button("Buscar na Biblioteca"):
        with st.spinner('Procurando na nuvem...'):
            st.session_state["resultados"] = buscar_musicas(termo)
    
    if "resultados" in st.session_state:
        selecionada = st.selectbox("Selecione a música:", st.session_state["resultados"])
        if st.button("Adicionar à Lista"):
            st.success(f"Adicionado: {selecionada}")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Sair"):
        st.session_state["prestador_id"] = None
        st.rerun()
