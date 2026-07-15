import streamlit as st
import qrcode
import re
import unicodedata
import cloudinary
import cloudinary.api
from io import BytesIO
import requests

# ... (Configuração Cloudinary e normalizar_nome igual ao seu)

def encontrar_link_real(nome_base):
    try:
        resources = cloudinary.api.resources(type="upload", resource_type="video", prefix=nome_base, max_results=1)
        if resources['resources']:
            url = resources['resources'][0]['secure_url']
            return url.replace("/upload/", "/upload/fl_attachment/") + ".mp4"
    except: return None

# ... (Seu bloco de Login permanece igual)

# No bloco onde lista os pedidos, adicione os controlos:
if col3.button("🎤", key=f"start_{p_id}"):
    link_real = encontrar_link_real(normalizar_nome(p.get('musica')))
    if link_real:
        requests.put(url_status, json={
            "acao": "contagem", 
            "cantor": p.get('cantor'), 
            "musica": p.get('musica'),
            "url_video": link_real,
            "comando": "play"
        })
        st.rerun()

# --- NOVA SECÇÃO DE CONTROLO ---
st.divider()
st.subheader("🎮 Controlo Remoto da TV")
col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
if col_c1.button("⏸️ Pause"): requests.patch(url_status, json={"comando": "pause"})
if col_c2.button("▶️ Play"): requests.patch(url_status, json={"comando": "play"})
if col_c3.button("🔄 Repetir"): requests.patch(url_status, json={"comando": "repeat"})
if col_c4.button("⏪ -10s"): requests.patch(url_status, json={"comando": "voltar"})
if col_c5.button("⏩ +10s"): requests.patch(url_status, json={"comando": "avancar"})
