import streamlit as st
import requests
import time
import qrcode
from io import BytesIO
import re
import unicodedata
import cloudinary.api

# Configuração Cloudinary
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"

st.set_page_config(page_title="Painel do Prestador", layout="wide")

def normalizar_nome(nome):
    nome = nome.replace(".mp4", "").replace("PEDIDO: ", "")
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = re.sub(r'[^\w\s]', '', nome)
    return "_".join(nome.split())

def encontrar_link_real(nome_base):
    try:
        resources = cloudinary.api.resources(type="upload", resource_type="video", prefix=nome_base, max_results=1)
        return resources['resources'][0]['secure_url'] if resources['resources'] else None
    except: return None

if "nome" not in st.session_state: st.session_state.nome = None

if st.session_state.nome is None:
    st.title("🎤 Portal do Prestador")
    with st.form("login"):
        n = st.text_input("Nome"); s = st.text_input("Sobrenome"); t = st.text_input("Telefone")
        if st.form_submit_button("Entrar"):
            slug = f"{n.lower()}-{s.lower()}"
            st.session_state.nome = f"{n} {s}"; st.session_state.slug = slug
            st.rerun()
else:
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"nome": None}))
    st.title(f"Bem-vindo, {st.session_state.nome}")
    
    url_cli = f"https://appcliente.streamlit.app/?prestador={st.session_state.slug}"
    st.info(f"🔗 Cliente: {url_cli}")
    
    pedidos = requests.get(f"{BASE_URL}/pedidos_{st.session_state.slug}.json").json() or {}
    
    for p_id, p in pedidos.items():
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"🎤 {p['cantor']} - {p['musica']}")
        if c2.button("🗑️", key=f"d{p_id}"): requests.delete(f"{BASE_URL}/pedidos_{st.session_state.slug}/{p_id}.json"); st.rerun()
        if c3.button("🎤", key=f"s{p_id}"):
            link = encontrar_link_real(normalizar_nome(p['musica']))
            requests.put(f"{BASE_URL}/status_{st.session_state.slug}.json", json={
                "cantor": p['cantor'], "musica": p['musica'], "url_video": link, "comando": "aguardando_play"
            })
            st.rerun()
    
    if st.button("▶️ FORÇAR PLAY"): requests.patch(f"{BASE_URL}/status_{st.session_state.slug}.json", json={"comando": "play"}); st.rerun()
    time.sleep(2); st.rerun()
