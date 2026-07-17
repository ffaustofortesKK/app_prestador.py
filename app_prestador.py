import streamlit as st
import re
import unicodedata
import cloudinary
import cloudinary.api
import requests
import time

# Configuração Cloudinary
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="Painel do Prestador", layout="wide")

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"

# --- FUNÇÕES ---
def normalizar_nome(nome):
    nome = nome.replace(".mp4", "").replace("PEDIDO: ", "")
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = re.sub(r'[^\w\s]', '', nome)
    return "_".join(nome.split())

def encontrar_link_real(nome_base):
    try:
        resources = cloudinary.api.resources(type="upload", resource_type="video", prefix=nome_base, max_results=1)
        if resources['resources']: return resources['resources'][0]['secure_url']
    except: return None

# --- ESTRUTURA ---
if "nome" not in st.session_state: st.session_state.nome = None

if st.session_state.nome is None:
    st.title("🎤 Portal do Prestador")
    with st.form("login"):
        n = st.text_input("Nome"); s = st.text_input("Sobrenome"); t = st.text_input("Telefone")
        if st.form_submit_button("Entrar"):
            st.session_state.nome = f"{n} {s}"; st.session_state.slug = f"{n.lower()}-{s.lower()}"
            st.rerun()
else:
    st.title(f"Gestão: {st.session_state.nome}")
    slug = st.session_state.slug
    
    # Buscar pedidos
    pedidos = requests.get(f"{BASE_URL}/pedidos_{slug}.json").json() or {}
    
    st.subheader("Fila de Pedidos")
    for p_id, p in pedidos.items():
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{p['cantor']}** - {p['musica']}")
        
        # Botão CHAMAR CANTOR
        if col2.button("🎤 Chamar", key=f"chamar_{p_id}"):
            link = encontrar_link_real(normalizar_nome(p['musica']))
            # CORREÇÃO: Enviando o comando exato para o cliente identificar
            payload = {
                "cantor": p['cantor'], 
                "musica": p['musica'], 
                "url_video": link, 
                "comando": "aguardando_play"
            }
            requests.put(f"{BASE_URL}/status_{slug}.json", json=payload)
            st.success(f"Chamando {p['cantor']}...")
            time.sleep(1); st.rerun()
            
        if col3.button("🗑️", key=f"del_{p_id}"):
            requests.delete(f"{BASE_URL}/pedidos_{slug}/{p_id}.json")
            st.rerun()

    if st.sidebar.button("Sair"): st.session_state.nome = None; st.rerun()
