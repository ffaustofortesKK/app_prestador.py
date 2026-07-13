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

if "prestador_id" not in st.session_state: st.session_state.prestador_id = None

# --- LOGIN / REGISTRO AUTOMÁTICO ---
if st.session_state.prestador_id is None:
    st.title("🎤 Portal do Prestador")
    
    # Campos obrigatórios
    nome = st.text_input("Nome:")
    sobrenome = st.text_input("Sobrenome:")
    telef = st.text_input("Telefone:")
    
    if st.button("Entrar"):
        # Validação de preenchimento obrigatório
        if nome and sobrenome and telef:
            # 1. Tenta buscar o prestador pelo telefone
            res = supabase.table("prestadores").select("*").eq("telefone", telef).execute()
            
            if res.data:
                # Prestador existe, faz login
                st.session_state.update({
                    "prestador_id": res.data[0]["id"],
                    "nome": f"{nome} {sobrenome}",
                    "slug": res.data[0]["slug_unico"]
                })
                st.rerun()
            else:
                # 2. Prestador não existe, cria novo registro automaticamente
                slug_novo = f"{nome.lower()}-{sobrenome.lower()}"
                novo_prestador = {
                    "nome_prestador": f"{nome} {sobrenome}",
                    "telefone": telef,
                    "slug_unico": slug_novo
                }
                
                try:
                    insert_res = supabase.table("prestadores").insert(novo_prestador).execute()
                    # Após criar, busca o ID gerado
                    res = supabase.table("prestadores").select("*").eq("telefone", telef).execute()
                    st.session_state.update({
                        "prestador_id": res.data[0]["id"],
                        "nome": f"{nome} {sobrenome}",
                        "slug": slug_novo
                    })
                    st.success("Cadastro realizado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao registrar: {e}")
        else:
            st.error("⚠️ Por favor, preencha NOME, SOBRENOME e TELEFONE para continuar.")

else:
    # --- PAINEL PRINCIPAL ---
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    url_cliente = f"https://ffkaraoke-cliente.streamlit.app/?prestador={st.session_state.slug}"
    st.info("Link de acesso para seus clientes:")
    st.code(url_cliente)
    
    qr = qrcode.make(url_cliente)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    st.image(buf.getvalue(), width=150)

    st.subheader("📋 Pedidos Recebidos")
    if st.button("🔄 Atualizar Fila"):
        url_fila = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{st.session_state.slug}.json"
        try:
            pedidos = requests.get(url_fila).json()
            if pedidos:
                for chave, p in pedidos.items(): st.success(f"🎤 {p.get('cantor')}: {p.get('musica')}")
            else: st.write("Fila vazia.")
        except: st.error("Erro ao carregar pedidos.")

    if st.button("Sair"):
        st.session_state.prestador_id = None
        st.rerun()
