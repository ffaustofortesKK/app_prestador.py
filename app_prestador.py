import streamlit as st
import qrcode
from io import BytesIO
from supabase import create_client
import requests

# Configuração do Supabase
url = st.secrets["URL_SUPABASE"]
key = st.secrets["KEY_SUPABASE"]
supabase = create_client(url, key)

st.set_page_config(page_title="Painel do Prestador", layout="centered")

# Inicializar sessão
if "prestador_id" not in st.session_state: st.session_state.prestador_id = None

# --- LOGIN SEM SENHA ---
if st.session_state.prestador_id is None:
    st.title("🎤 Portal do Prestador")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome:")
        sobrenome = st.text_input("Sobrenome:")
    telef = st.text_input("Telefone:")
    
    if st.button("Entrar"):
        if nome and telef:
            # Busca o prestador no Supabase pelo telefone
            res = supabase.table("prestadores").select("*").eq("telefone", telef).execute()
            if res.data:
                st.session_state.update({
                    "prestador_id": res.data[0]["id"],
                    "nome": f"{nome} {sobrenome}",
                    "slug": res.data[0]["slug_unico"]
                })
                st.rerun()
            else:
                st.error("Prestador não encontrado. Verifique o número de telefone.")
        else:
            st.warning("Preencha todos os campos!")
else:
    # --- PAINEL PRINCIPAL ---
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    url_cliente = f"https://ffkaraoke-cliente.streamlit.app/?prestador={st.session_state.slug}"
    st.info("Link de acesso para seus clientes:")
    st.code(url_cliente)
    
    # Gerar QR Code
    qr = qrcode.make(url_cliente)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    st.image(buf.getvalue(), width=150)

    st.subheader("📋 Pedidos Recebidos")
    if st.button("🔄 Atualizar"):
        url_fila = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{st.session_state.slug}.json"
        try:
            pedidos = requests.get(url_fila).json()
            if pedidos:
                for chave, p in pedidos.items(): st.success(f"🎤 {p.get('cantor')}: {p.get('musica')}")
            else: st.write("Fila vazia.")
        except: st.error("Erro ao buscar fila.")

    if st.button("Sair"):
        st.session_state.prestador_id = None
        st.rerun()
