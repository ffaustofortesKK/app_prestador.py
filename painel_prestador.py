import streamlit as st

# --- TELA DO PAINEL (Interface Personalizada) ---
else:
    # 1. Estilização CSS (tem que ficar dentro do else para ser aplicada)
    st.markdown("""
        <style>
        .big-box { background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; }
        .sintonia-box { background-color: #260000; padding: 15px; border-radius: 5px; border: 1px solid #ff4b4b; }
        </style>
    """, unsafe_allow_html=True)

    # 2. Cabeçalho
    st.markdown("## 🎤 PAINEL DE CONTROLE")
    
    # 3. Caixa de Adicionar Música
    with st.container():
        st.markdown('<div class="big-box">', unsafe_allow_html=True)
        nome_cantor = st.text_input("Nome do Cantor:")
        musica = st.text_input("Nome da Música:")
        
        if st.button("★ ADICIONAR À LISTA LOCAL", use_container_width=True):
            st.success("Música enviada!")
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. Fila
    st.subheader("FILA DE REPRODUÇÃO ATUAL:")
    st.write("1. Exemplo de Música")
    
    col1, col2, col3 = st.columns(3)
    col1.button("↑ Subir")
    col2.button("↓ Descer")
    col3.button("🗑️ Remover")
    
    st.button("▶ ANUNCIAR PRÓXIMO CANTOR", use_container_width=True, type="primary")

    # 5. Sintonia Cloud
    st.markdown('<div class="sintonia-box">', unsafe_allow_html=True)
    st.write("### SISTEMA EM SINTONIA CLOUD")
    c1, c2 = st.columns(2)
    c1.button("✅ Validar", use_container_width=True)
    c2.button("🗑️ Recusar", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Sair"):
        st.session_state["prestador"] = None
        st.rerun()
