import streamlit as st
from supabase import create_client, Client
import bcrypt
import json

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def registrar_usuario(username: str, password: str):
    supabase = get_supabase()
    res = supabase.table("usuarios").select("id").eq("username", username).execute()
    if res.data:
        return False, "Nome de usuário já cadastrado!"
    
    pwd_hash = hash_password(password)
    supabase.table("usuarios").insert({"username": username, "password_hash": pwd_hash}).execute()
    return True, "Conta criada com sucesso! Faça login abaixo."

def autenticar_usuario(username: str, password: str):
    supabase = get_supabase()
    res = supabase.table("usuarios").select("*").eq("username", username).execute()
    if not res.data:
        return False, "Usuário não encontrado."
    
    user_data = res.data[0]
    if check_password(password, user_data["password_hash"]):
        return True, user_data
    return False, "Senha incorreta."

def render_login_screen():
    st.markdown("<h2 style='text-align: center;'>🛡️ Forja de Heróis — Acesso</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        with tab_login:
            with st.form("form_login"):
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                btn_entrar = st.form_submit_button("Entrar no Grimoire", use_container_width=True)
                
                if btn_entrar:
                    sucesso, res = autenticar_usuario(usuario, senha)
                    if sucesso:
                        st.session_state["logged_in"] = True
                        st.session_state["user_id"] = res["id"]
                        st.session_state["username"] = res["username"]
                        st.success(f"Bem-vindo, {res['username']}!")
                        st.rerun()
                    else:
                        st.error(res)

        with tab_cadastro:
            with st.form("form_cadastro"):
                novo_usuario = st.text_input("Escolha um Nome de Usuário")
                nova_senha = st.text_input("Escolha uma Senha", type="password")
                btn_cadastrar = st.form_submit_button("Criar Minha Conta", use_container_width=True)
                
                if btn_cadastrar:
                    if len(novo_usuario) < 3 or len(nova_senha) < 4:
                        st.warning("Usuário e senha devem ser mais longos.")
                    else:
                        ok, msg = registrar_usuario(novo_usuario, nova_senha)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)