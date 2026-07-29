import streamlit as st

# Configuração da página Streamlit (deve ser a primeira chamada Streamlit)
st.set_page_config(
    page_title="Forja de Heróis — Fichas D&D 5e (2024)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.database import init_db, load_character
from src.pdf_parser import ensure_docs_folder
from src.ui.styles import apply_grimoire_theme
from src.ui.dashboard import render_dashboard
from src.ui.wizard import render_character_wizard
from src.ui.character_sheet import render_character_sheet

def main():
    # 1. Inicializa pastas, banco de dados e tema
    ensure_docs_folder()
    init_db()
    apply_grimoire_theme()

    # 2. Gerenciamento do estado da navegação
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

    # 3. Roteamento das Telas
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
