import streamlit as st
import qrcode
from io import BytesIO
from supabase import create_client
import requests

# --- DICIONÁRIO DE MÚSICAS (Substitua pelos seus links reais do Cloudinary) ---
BIBLIOTECA_VIDEOS = {
    "Sittin On The Dock": "https://res.cloudinary.com/SEU_CLOUD_NAME/video/upload/v1234567890/Sittin_On_The_Dock.mp4",
    "Outra Musica": "https://res.cloudinary.com/SEU_CLOUD_NAME/video/upload/v1234567890/outra_musica.mp4",
    # Adicione aqui todas as músicas conforme elas estiverem no seu Cloudinary
}

# Configuração Supabase
url = st.secrets["URL_SUPABASE"]
key = st.secrets["KEY_SUPABASE"]
supabase = create_client(url, key)

st.set_page_config(page_title="Painel do Prestador", layout="wide")

# Inicialização segura
if "prestador_id" not in st.session_state: st.session_state.prestador_id = None
if "nome" not in st.session_state: st.session_state.nome = None
if "slug" not in st.session_state: st.session_state.slug = None

# --- LOGIN / REGISTRO ---
# (O código de login permanece igual ao que já tinha...)
if st.session_state.prestador_id is None:
    st.title("🎤 Portal do Prestador")
    nome_input = st.text_input("Nome:")
    sobrenome_input = st.text_input("Sobrenome:") 
    telef = st.text_input("Telefone:")
    
    if st.button("Entrar"):
        if nome_input and sobrenome_input and telef:
            try:
                res = supabase.table("prestadores").select("*").eq("telefone", telef).execute()
                if res.data and len(res.data) > 0:
                    st.session_state.update({"prestador_id": res.data[0]["id"], "nome": f"{nome_input} {sobrenome_input}", "slug": res.data[0]["slug_unico"]})
                    st.rerun()
                else:
                    slug_novo = f"{nome_input.lower()}-{sobrenome_input.lower()}"
                    supabase.table("prestadores").insert({"Nome": nome_input, "Sobrenome": sobrenome_input, "telefone": telef, "slug_unico": slug_novo}).execute()
                    st.session_state.update({"nome": f"{nome_input} {sobrenome_input}", "slug": slug_novo})
                    st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    # ... (QR Code e links permanecem iguais) ...
    
    st.divider()
    st.subheader("📋 Gestão de Fila")
    
    base_url = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
    url_fila = f"{base_url}/pedidos_{st.session_state.slug}.json"
    url_status = f"{base_url}/status_{st.session_state.slug}.json"
    
    try:
        pedidos_data = requests.get(url_fila).json()
        if pedidos_data:
            for p_id, p in pedidos_data.items():
                col1, col2, col3 = st.columns([4, 1, 1])
                musica_nome = p.get('musica')
                col1.write(f"🎤 {p.get('cantor')} - {musica_nome}")
                
                if col2.button("🗑️", key=f"del_{p_id}"):
                    requests.delete(f"{base_url}/pedidos_{st.session_state.slug}/{p_id}.json")
                    st.rerun()
                
                if col3.button("🎤", key=f"start_{p_id}", help="Anunciar na TV"):
                    # BUSCA AUTOMÁTICA DO LINK
                    video_link = BIBLIOTECA_VIDEOS.get(musica_nome, "ERRO_LINK_NAO_ENCONTRADO")
                    
                    requests.put(url_status, json={
                        "acao": "contagem", 
                        "cantor": p.get('cantor'), 
                        "musica": musica_nome,
                        "url_video": video_link
                    })
                    
                    if video_link == "ERRO_LINK_NAO_ENCONTRADO":
                        st.warning(f"Atenção: Vídeo para '{musica_nome}' não encontrado no Cloudinary!")
                    else:
                        st.success("Enviado para TV!")
                    st.rerun()
        else: 
            st.write("Fila vazia.")
    except Exception as e:
        st.error(f"Erro ao conectar com a fila: {e}")
