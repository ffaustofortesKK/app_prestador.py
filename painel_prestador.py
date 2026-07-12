import streamlit as st
import qrcode
from io import BytesIO
from supabase import create_client

# Configuração do Supabase
url = st.secrets["URL_SUPABASE"]
key = st.secrets["KEY_SUPABASE"]
supabase = create_client(url, key)

st.set_page_config(page_title="Painel do Prestador", layout="centered")

# Inicializar sessão
if "prestador_id" not in st.session_state:
    st.session_state["prestador_id"] = None

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .big-box { background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; color: white; }
    .sintonia-box { background-color: #260000; padding: 15px; border-radius: 5px; border: 1px solid #ff4b4b; color: white; }
    </style>
""", unsafe_allow_html=True)

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

# --- PAINEL (APÓS LOGIN) ---
else:
    st.markdown(f"## 🎤 Bem-vindo, {st.session_state['nome']}!")
    
    # Gerar link personalizado
    slug = st.session_state["slug"]
    url_cliente = f"https://ffkaraoke-cliente.streamlit.app/?prestador={slug}"
    
    st.success(f"Seu link personalizado: {url_cliente}")
    
    # Gerar QR Code
    qr = qrcode.make(url_cliente)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="QR Code para seus clientes")

    # Interface Visual
    st.markdown('<div class="big-box">', unsafe_allow_html=True)
    nome_cantor = st.text_input("Nome do Cantor:")
    musica = st.text_input("Nome da Música:")
    if st.button("★ ADICIONAR À LISTA LOCAL", use_container_width=True):
        st.success("Música adicionada!")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("FILA DE REPRODUÇÃO ATUAL:")
    col1, col2, col3 = st.columns(3)
    col1.button("↑ Subir")
    col2.button("↓ Descer")
    col3.button("🗑️ Remover")
    
    st.button("▶ ANUNCIAR PRÓXIMO CANTOR", use_container_width=True, type="primary")

    # Área Cloud
    st.markdown('<div class="sintonia-box">', unsafe_allow_html=True)
    st.write("### SISTEMA EM SINTONIA CLOUD")
    c1, c2 = st.columns(2)
    c1.button("✅ Validar", use_container_width=True)
    c2.button("🗑️ Recusar", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Sair"):
        st.session_state["prestador_id"] = None
        st.rerun()
