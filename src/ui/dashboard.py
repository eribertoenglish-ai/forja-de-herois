import json
import base64
import streamlit as st
from src.database import list_characters, delete_character, duplicate_character, save_character
from src.models import Character
from src.pdf_parser import scan_and_parse_pdf_docs, ensure_docs_folder

def render_dashboard(on_open_character, on_create_new):
    """Renderiza o Painel Inicial com cartões de personagens salvos e ações do sistema."""
    st.markdown("# 🛡️ FORJA DE HERÓIS")
    st.markdown("##### *Gerenciador Oficial de Fichas de Personagem D&D 5e (Regras 2024)*")
    st.markdown("---")

    ensure_docs_folder()

    # Barra Superior de Ações
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([2, 2, 2, 2])
    with col_btn1:
        if st.button("➕ CRIAR NOVO PERSONAGEM", use_container_width=True):
            on_create_new()
    with col_btn2:
        uploaded_json = st.file_uploader("Importar Backup (JSON)", type=["json"], label_visibility="collapsed")
        if uploaded_json is not None:
            try:
                content = json.load(uploaded_json)
                imported_char = Character.from_dict(content)
                imported_char.id = None
                new_id = save_character(imported_char)
                st.success(f"Personagem '{imported_char.name}' importado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao importar JSON: {e}")
    with col_btn3:
        if st.button("📖 ESCANEAR PDFs (./docs/)", use_container_width=True):
            with st.spinner("Escaneando arquivos PDF em ./docs/..."):
                res = scan_and_parse_pdf_docs()
                if res.get("status") == 0:
                    st.info(res.get("msg", "Nenhum PDF processado."))
                else:
                    st.success(f"PDFs escaneados! Magias adicionadas: {res.get('spells', 0)}")
    with col_btn4:
        st.markdown("<span class='badge-gold'>D&D 5e 2024 Offline</span>", unsafe_allow_html=True)

    st.markdown("### 📜 Personagens Cadastrados")

    characters = list_characters()

    if not characters:
        st.info("Nenhum personagem cadastrado ainda. Clique em **➕ CRIAR NOVO PERSONAGEM** para começar sua aventura!")
        return

    # Exibição em Grid de Cartões (2 colunas)
    cols = st.columns(2)
    for idx, c in enumerate(characters):
        col = cols[idx % 2]
        char_obj: Character = c["character_obj"]

        with col:
            st.markdown(f"""
            <div class="grimoire-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #D97706;">{c['name']}</h3>
                    <span class="badge-gold">Nível {c['total_level']}</span>
                </div>
                <p style="margin-top: 4px; font-size: 0.9rem; color: #A1A1AA;">
                    <b>Sistema:</b> D&D 5e (2024) | <b>Campanha:</b> {c['campaign'] or 'Padrão'}
                </p>
                <p style="margin-top: 2px; font-size: 0.9rem; color: #E4E4E7;">
                    <b>Espécie:</b> {c['species']} | <b>Classe(s):</b> {c['classes_str']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Botões de Ação do Cartão
            bcol1, bcol2, bcol3, bcol4 = st.columns(4)
            with bcol1:
                if st.button("📖 ABRIR", key=f"open_{c['id']}", use_container_width=True):
                    on_open_character(c["id"])
            with bcol2:
                if st.button("📋 DUPLICAR", key=f"dup_{c['id']}", use_container_width=True):
                    duplicate_character(c["id"])
                    st.toast(f"Cópia de '{c['name']}' criada!")
                    st.rerun()
            with bcol3:
                # Botão para baixar backup JSON
                char_json = json.dumps(char_obj.to_dict(), indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 BACKUP",
                    data=char_json,
                    file_name=f"personagem_{c['id']}_{c['name'].replace(' ', '_')}.json",
                    mime="application/json",
                    key=f"dl_{c['id']}",
                    use_container_width=True
                )
            with bcol4:
                if st.button("🗑️ EXCLUIR", key=f"del_{c['id']}", use_container_width=True):
                    delete_character(c["id"])
                    st.toast(f"Personagem '{c['name']}' excluído.")
                    st.rerun()

            st.markdown("<br/>", unsafe_allow_html=True)
