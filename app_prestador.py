import streamlit as st
import qrcode
import re
import unicodedata
import cloudinary
import cloudinary.api
from io import BytesIO
import requests
import time

cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="Painel do Prestador", layout="wide")

if "nome" not in st.session_state: st.session_state.nome = None
if "slug" not in st.session_state: st.session_state.slug = None

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"

def normalizar_nome(nome):
    nome = nome.replace(".mp4", "").replace("PEDIDO:", "")
    nome = re.sub(r'["\'()\[\]]', '', nome)
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = re.sub(r'[^\w\s]', '', nome)
    return "_".join(nome.split())

def encontrar_link_real(nome_base):
    try:
        resources = cloudinary.api.resources(type="upload", resource_type="video", prefix=nome_base, max_results=1)
        return resources['resources'][0]['secure_url'] if resources['resources'] else None
    except: return None

if st.session_state.nome is None:
    st.title("🎤 Portal do Prestador")
    with st.form("login_form"):
        n = st.text_input("Nome:"); s = st.text_input("Sobrenome:"); t = st.text_input("Telefone:")
        if st.form_submit_button("Entrar"):
            if n and s and t:
                st.session_state.nome = f"{n} {s}"; st.session_state.slug = f"{n.lower()}-{s.lower()}"
                st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    url_cliente = f"https://appcliente.streamlit.app/?prestador={st.session_state.slug}"
    st.info(f"🔗 **Cliente:** {url_cliente}")
    
    url_status = f"{BASE_URL}/status_{st.session_state.slug}.json"
    pedidos_data = requests.get(f"{BASE_URL}/pedidos_{st.session_state.slug}.json").json() or {}
    
    if pedidos_data:
        for p_id, p in pedidos_data.items():
            col1, col2 = st.columns([3, 1])
            col1.write(f"🎤 {p.get('cantor')} - {p.get('musica')}")
            if col2.button("🎤 Iniciar", key=f"start_{p_id}"):
                link = encontrar_link_real(normalizar_nome(p.get('musica')))
                requests.put(url_status, json={
                    "cantor": p.get('cantor'), "musica": p.get('musica'), 
                    "url_video": link, "comando": "aguardando_play"
                })
                st.rerun()
    time.sleep(3); st.rerun()
