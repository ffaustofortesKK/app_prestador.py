import streamlit as st
import requests
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# CSS para o fundo da TV e esconder elementos do Streamlit
st.markdown("""
    <style>
        .stApp { 
            background: url('https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=2074&auto=format&fit=crop'); 
            background-size: cover; 
            background-position: center;
        }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        .fila-container { background: rgba(0,0,0,0.7); padding: 30px; border-radius: 20px; color: white; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")
if not slug: st.error("URL Inválida"); st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

display = st.empty()
video_atual = ""

while True:
    try:
        # Busca status e pedidos
        status = requests.get(URL_STATUS, timeout=5).json()
        pedidos = requests.get(URL_PEDIDOS, timeout=5).json()
        
        # Verifica se há vídeo para tocar (comando 'play')
        if isinstance(status, dict) and status.get("url_video") and status.get("comando") == "play":
            nova_url = status.get('url_video')
            
            components.html(f"""
                <div style='text-align: center; background: black; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                    <h1 style='color: yellow;'>SOLTA A VOZ: {status.get('cantor', 'CANTOR').upper()}</h1>
                    <video id="v1" width="800" autoplay playsinline style="border: 10px solid #FFD700; border-radius: 20px;">
                        <source src="{nova_url}" type="video/mp4">
                    </video>
                </div>
                <script>
                    var vid = document.getElementById('v1');
                    vid.play();
                    
                    // Quando o vídeo acaba, volta para a tela de espera
                    vid.onended = function() {{ 
                        fetch('{URL_STATUS}', {{ method: 'PATCH', body: JSON.stringify({{comando: 'stop'}}) }})
                        .then(() => {{ window.location.reload(); }});
                    }};
                    
                    document.body.addEventListener('click', () => {{ vid.play(); vid.muted = false; }});
                </script>
            """, height=800)
        else:
            # Tela de Espera com Lista de Pedidos
            with display.container():
                st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px #000; margin-top: 50px;'>AGUARDANDO PRÓXIMO CANTOR...</h1>", unsafe_allow_html=True)
                
                if pedidos and isinstance(pedidos, dict):
                    st.markdown("<div class='fila-container'>", unsafe_allow_html=True)
                    st.subheader("📋 FILA DE ESPERA:")
                    for i, (p_id, p) in enumerate(pedidos.items(), 1):
                        st.markdown(f"<h2>{i}. {p.get('cantor')} - {p.get('musica')}</h2>")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='fila-container'><h2>Fila vazia. Aguardando novos pedidos!</h2></div>", unsafe_allow_html=True)
    
    except Exception as e:
        display.warning("Aguardando conexão com o servidor...")
        
    time.sleep(3)
