import streamlit as st

# 1. Configuração da página (DEVE ser a PRIMEIRA chamada do Streamlit)
st.set_page_config(
    page_title="Forja de Heróis — Fichas D&D 5e (2024)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Na barra lateral ou onde achar melhor
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Material de Consulta")

st.sidebar.link_button(
    label="📖 Abrir Livro de Regras (PDF)",
    url="https://drive.google.com/file/d/1OvDHpap5QTJMles57zNyAZFv-tQrWxuu/view?usp=sharing",
    use_container_width=True
)

# 2. Injeção PWA para o PWABuilder / App Celular
pwa_code = """
<link rel="manifest" href="data:application/json;base64,ewogICJuYW1lIjogIkZvcmphIGRlIEhlcvNpc2siLAogICJzaG9ydF9uYW1lIjogIkZvcmphSGVy82lzIiwKICAic3RhcnRfdXJsIjogIi8iLAogICJkaXNwbGF5IjogInN0YW5kYWxvbmUiLAogICJiYWNrZ3JvdW5kX2NvbG9yIjogIiMxMjEyMTQiLAogICJ0aGVtZV9jb2xvciI6ICIjRDk3NzA2IiwKICAiaWNvbnMiOiBbCiAgICB7CiAgICAgICJzcmMiOiAiaHR0cHM6Ly9zdGF0aWMuOTEyd2ViLmNvbS9mYXZpY29ucy9nb29nbGUucG5nIiwKICAgICAgInNpemVzIjogIjUxMng1MTIiLAogICAgICAidHlwZSI6ICJpbWFnZS9wbmciLAogICAgICAicHVycG9zZSI6ICJhbnkgbWFza2FibGUiCiAgICB9CiAgXQp9">
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('data:text/javascript;base64,c2VsZi5hZGRFdmVudExpc3RlbmVyKCdmZXRjaCcsIGZ1bmN0aW9uKGV2ZW50KSB7fSk7');
  });
}
</script>
"""
st.markdown(pwa_code, unsafe_allow_html=True)

# 3. Imports dos módulos do projeto
from src.database import init_db, load_character
from src.pdf_parser import ensure_docs_folder
from src.ui.styles import apply_grimoire_theme
from src.ui.dashboard import render_dashboard
from src.ui.wizard import render_character_wizard
from src.ui.character_sheet import render_character_sheet
from src.auth_db import render_login_screen

def main():
    # Inicializa pastas, banco e temas
    ensure_docs_folder()
    init_db()
    apply_grimoire_theme()

    # Controle de Sessão / Login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Se NÃO estiver logado, bloqueia a navegação e exibe a tela de Login
    if not st.session_state["logged_in"]:
        render_login_screen()
        return

    # Barra Superior do Jogador Logado
    col_user, col_logout = st.columns([8, 2])
    with col_user:
        st.caption(f"🎮 Mestre/Jogador: **{st.session_state.get('username', 'Convidado')}**")
    with col_logout:
        if st.button("🚪 Sair", key="btn_logout"):
            st.session_state["logged_in"] = False
            st.session_state.clear()
            st.rerun()

    # Gerenciamento do estado da navegação
    if "current_view" not in st.session_state:
        st.session_state.current_view = "dashboard"
    if "selected_char_id" not in st.session_state:
        st.session_state.selected_char_id = None

    # Callbacks de navegação
    def go_to_dashboard():
        st.session_state.current_view = "dashboard"
        st.session_state.selected_char_id = None
        st.rerun()

    def go_to_wizard():
        st.session_state.current_view = "wizard"
        st.rerun()

    def open_character(char_id: int):
        st.session_state.selected_char_id = char_id
        st.session_state.current_view = "character_sheet"
        st.rerun()

    # Roteamento das Telas
    current_view = st.session_state.current_view

    if current_view == "dashboard":
        render_dashboard(
            on_open_character=open_character,
            on_create_new=go_to_wizard
        )

    elif current_view == "wizard":
        render_character_wizard(
            on_finish=lambda new_id: open_character(new_id),
            on_cancel=go_to_dashboard
        )

    elif current_view == "character_sheet":
        char_id = st.session_state.selected_char_id
        char = load_character(char_id) if char_id else None
        if char:
            render_character_sheet(
                char=char,
                on_back_to_dashboard=go_to_dashboard
            )
        else:
            st.error("Personagem não encontrado.")
            if st.button("Voltar ao Painel"):
                go_to_dashboard()

if __name__ == "__main__":
    main()
