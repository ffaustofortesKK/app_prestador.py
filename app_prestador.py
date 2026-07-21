import streamlit as st
import requests
import time
import cloudinary
import cloudinary.search

# Configuração Cloudinary
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="FF KARAOKE - PAINEL DO PRESTADOR", layout="wide")

st.markdown("""
    <style>
        .stApp { background: #111; color: white; }
        .titulo { color: gold; text-align: center; font-weight: bold; }
        .card { background: #222; padding: 15px; border-radius: 8px; border: 1px solid #444; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

st.markdown(f"<h1 class='titulo'>🎛️ PAINEL DO PRESTADOR ({slug.upper()})</h1>", unsafe_allow_html=True)

# Buscar status atual do Firebase
try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

aba1, aba2, aba3 = st.tabs(["🎤 Fila de Espera", "📺 Vídeos Clipes (Fundo)", "⚙️ Controlo Geral"])

# ABA 1: FILA DE ESPERA
with aba1:
    st.subheader("Gestão da Fila de Espera")
    
    if res_pedidos:
        for p_id, p in list(res_pedidos.items()):
            if not str(p.get('musica', '')).startswith("PEDIDO:"):
                col_a, col_b, col_c = st.columns([3, 3, 2])
                with col_a:
                    st.write(f"**Cantor:** {p.get('cantor')}")
                with col_b:
                    st.write(f"**Música:** {p.get('musica')}")
                with col_c:
                    if st.button("Chamar ao Palco", key=f"chamar_{p_id}"):
                        requests.patch(URL_STATUS, json={
                            "comando": "aguardando_play",
                            "cantor": p.get('cantor'),
                            "musica": p.get('musica'),
                            "url_video": p.get('url_video')
                        })
                        # Opcional: remover da fila após chamar
                        requests.delete(f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}/{p_id}.json")
                        st.rerun()
                st.markdown("---")
    else:
        st.info("A fila de espera está vazia.")

# ABA 2: VÍDEOS CLIPES (Acesso às músicas/clipes do Cloudinary)
with aba2:
    st.subheader("Seleccionar Vídeo Clipe para o Fundo da TV")
    
    try:
        # Busca os ficheiros no Cloudinary
        result = cloudinary.search.search().expression("resource_type:video").max_results(50).execute()
        recursos = result.get("resources", [])
    except Exception as e:
        recursos = []
        st.error(f"Erro ao carregar vídeos do Cloudinary: {e}")

    if recursos:
        opcoes_videos = {r['public_id']: r['secure_url'] for r in recursos}
        escolha_clipe = st.selectbox("Escolha um Vídeo Clipe da Biblioteca:", list(opcoes_videos.keys()))
        
        if st.button("▶️ Enviar Clipe para a TV (Caixa da Direita)"):
            url_escolhida = opcoes_videos[escolha_clipe]
            requests.patch(URL_STATUS, json={
                "comando": "play_clipe",
                "cantor": "VÍDEO CLIPE",
                "musica": escolha_clipe,
                "url_video": url_escolhida
            })
            st.success(f"Vídeo clipe '{escolha_clipe}' enviado com sucesso para a TV!")
            st.rerun()
    else:
        st.warning("Nenhum vídeo encontrado na conta Cloudinary.")

# ABA 3: CONTROLO GERAL
with aba3:
    st.subheader("Comandos Manuais de Emergência")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏹️ Parar / Limpar Tela da TV", use_container_width=True):
            requests.patch(URL_STATUS, json={
                "comando": "fim",
                "url_video": "",
                "musica": "",
                "cantor": ""
            })
            st.success("Estado limpo na TV.")
            st.rerun()
            
    with col2:
        if st.button("🔄 Recarregar TV Remotamente", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "recarregar"})
            st.success("Comando enviado.")
            st.rerun()

    st.markdown("---")
    st.write("**Estado Atual na Base de Dados:**")
    st.json(res_status)
