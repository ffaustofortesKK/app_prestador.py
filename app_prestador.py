# --- NOVA CAIXA DE PEDIDOS MANUAIS ---
    st.markdown("---")
    st.subheader("⚠️ Pedidos Manuais (Atenção)")
    
    # Busca os pedidos manuais que começam com "PEDIDO:"
    pedidos_manuais = {k: v for k, v in pedidos_data.items() if str(v.get('musica', '')).startswith("PEDIDO:")}
    
    if pedidos_manuais:
        # Estilo para piscar em amarelo
        st.markdown("""
            <style>
                .blink {
                    animation: blinker 1s linear infinite;
                    color: yellow;
                    font-weight: bold;
                    background-color: rgba(255, 255, 0, 0.1);
                    padding: 10px;
                    border: 2px solid yellow;
                    border-radius: 10px;
                }
                @keyframes blinker { 50% { opacity: 0; } }
            </style>
        """, unsafe_allow_html=True)
        
        for p_id, p in pedidos_manuais.items():
            st.markdown(f'<div class="blink">📢 {p.get("cantor")}: {p.get("musica")}</div>', unsafe_allow_html=True)
            if st.button(f"Remover aviso {p_id[:4]}", key=f"del_man_{p_id}"):
                requests.delete(f"{BASE_URL}/pedidos_{st.session_state.slug}/{p_id}.json")
                st.rerun()
    else:
        st.success("Nenhum pedido manual pendente.")
