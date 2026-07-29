import random
import datetime
import streamlit as st
from src.database import fetch_all_species, fetch_all_classes, fetch_all_backgrounds, fetch_all_origin_feats, save_character
from src.models import Character, AttributeScores, ClassLevelInfo, EvolutionLogEntry
from src.rules_2024 import CLASS_HIT_DICE, CLASS_SAVING_THROWS, get_class_features_by_level

def render_character_wizard(on_finish, on_cancel):
    """Assistente de Criação de Personagem em 3 Passos (Wizard)."""
    st.markdown("# 🪄 CRIÇÃO DE PERSONAGEM D&D 5e (2024)")
    st.markdown("---")

    # Inicializa estado do wizard na sessão
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
    if "wizard_data" not in st.session_state:
        st.session_state.wizard_data = {
            "name": "Novo Herói",
            "campaign": "Campanha D&D 2024",
            "alignment": "Neutro e Bom",
            "languages": "Comum, Élfico",
            "attr_method": "Conjunto Padrão (15,14,13,12,10,8)",
            "attributes": AttributeScores(FOR=15, DES=14, CON=13, INT=12, SAB=10, CAR=8),
            "species": "Humano",
            "initial_class": "Guerreiro",
            "background": "Soldado",
            "origin_feat": "Combatente Forte"
        }

    w_data = st.session_state.wizard_data
    step = st.session_state.wizard_step

    # Indicador Visual de Passos
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <span class="{'badge-gold' if step == 1 else 'badge-dark'}">Passo 1: Informações Básicas</span>
        <span class="{'badge-gold' if step == 2 else 'badge-dark'}">Passo 2: Atributos</span>
        <span class="{'badge-gold' if step == 3 else 'badge-dark'}">Passo 3: Espécie, Classe & Antecedente</span>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # PASSO 1: INFORMAÇÕES BÁSICAS
    # ----------------------------------------------------
    if step == 1:
        st.markdown("### Passo 1: Informações Básicas do Herói")
        c1, c2 = st.columns(2)
        with c1:
            w_data["name"] = st.text_input("Nome do Personagem", value=w_data["name"])
            w_data["campaign"] = st.text_input("Nome da Campanha", value=w_data["campaign"])
        with c2:
            w_data["alignment"] = st.selectbox("Tendência", [
                "Leal e Bom", "Neutro e Bom", "Caótico e Bom",
                "Leal e Neutro", "Neutro Puro", "Caótico e Neutro",
                "Leal e Mau", "Neutro e Mau", "Caótico e Mau"
            ], index=1)
            w_data["languages"] = st.text_input("Idiomas Conhecidos", value=w_data["languages"])

        st.markdown("<br/>", unsafe_allow_html=True)
        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.button("❌ CANCELAR", use_container_width=True):
                on_cancel()
        with col_nav2:
            if st.button("PRÓXIMO: ATRIBUTOS ➡️", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()

    # ----------------------------------------------------
    # PASSO 2: GERAÇÃO DE ATRIBUTOS
    # ----------------------------------------------------
    elif step == 2:
        st.markdown("### Passo 2: Definição dos Atributos")
        method = st.radio("Método de Definição de Atributos", [
            "Conjunto Padrão (15, 14, 13, 12, 10, 8)",
            "Compra de Pontos (Point Buy - 27 pts)",
            "Rolagem de Dados (4d6 e descarta o menor)"
        ])
        w_data["attr_method"] = method

        attrs = w_data["attributes"]

        if method.startswith("Conjunto Padrão"):
            st.info("Atribua cada um dos valores do conjunto (15, 14, 13, 12, 10, 8) aos seus atributos:")
            std_values = [15, 14, 13, 12, 10, 8]
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1: attrs.FOR = st.selectbox("FOR", std_values, index=0)
            with c2: attrs.DES = st.selectbox("DES", std_values, index=1)
            with c3: attrs.CON = st.selectbox("CON", std_values, index=2)
            with c4: attrs.INT = st.selectbox("INT", std_values, index=3)
            with c5: attrs.SAB = st.selectbox("SAB", std_values, index=4)
            with c6: attrs.CAR = st.selectbox("CAR", std_values, index=5)

        elif method.startswith("Compra de Pontos"):
            st.info("Distribua os valores (8 a 15). Custo de Pontos (Total 27 pts):")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1: attrs.FOR = st.number_input("FOR", min_value=8, max_value=15, value=15)
            with c2: attrs.DES = st.number_input("DES", min_value=8, max_value=15, value=14)
            with c3: attrs.CON = st.number_input("CON", min_value=8, max_value=15, value=13)
            with c4: attrs.INT = st.number_input("INT", min_value=8, max_value=15, value=12)
            with c5: attrs.SAB = st.number_input("SAB", min_value=8, max_value=15, value=10)
            with c6: attrs.CAR = st.number_input("CAR", min_value=8, max_value=15, value=8)

            # Validação simples do custo de compra de pontos
            cost_table = {8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9}
            total_cost = sum(cost_table.get(v, 0) for v in [attrs.FOR, attrs.DES, attrs.CON, attrs.INT, attrs.SAB, attrs.CAR])
            st.caption(f"Pontos Gasto: **{total_cost} / 27 pts**")

        else: # Rolagem 4d6-menor
            st.info("Clique no botão abaixo para rolar 4d6 e descartar o menor dado para cada um dos 6 atributos.")
            if st.button("🎲 ROLAR 4d6 (DESCARTAR MENOR)"):
                def roll_4d6():
                    dice = [random.randint(1, 6) for _ in range(4)]
                    return sum(sorted(dice)[1:])
                attrs.FOR = roll_4d6()
                attrs.DES = roll_4d6()
                attrs.CON = roll_4d6()
                attrs.INT = roll_4d6()
                attrs.SAB = roll_4d6()
                attrs.CAR = roll_4d6()
                st.toast("Atributos rolados com sucesso!")

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1: st.metric("FOR", f"{attrs.FOR} ({attrs.modifier('FOR'):+d})")
            with c2: st.metric("DES", f"{attrs.DES} ({attrs.modifier('DES'):+d})")
            with c3: st.metric("CON", f"{attrs.CON} ({attrs.modifier('CON'):+d})")
            with c4: st.metric("INT", f"{attrs.INT} ({attrs.modifier('INT'):+d})")
            with c5: st.metric("SAB", f"{attrs.SAB} ({attrs.modifier('SAB'):+d})")
            with c6: st.metric("CAR", f"{attrs.CAR} ({attrs.modifier('CAR'):+d})")

        st.markdown("<br/>", unsafe_allow_html=True)
        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.button("⬅️ VOLTAR", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
        with col_nav2:
            if st.button("PRÓXIMO: ORIGENS ➡️", use_container_width=True):
                st.session_state.wizard_step = 3
                st.rerun()

    # ----------------------------------------------------
    # PASSO 3: ESPÉCIE, CLASSE E ANTECEDENTE 2024
    # ----------------------------------------------------
    elif step == 3:
        st.markdown("### Passo 3: Escolha de Espécie, Classe e Antecedente (Regras 2024)")

        species_options = [s["name"] for s in fetch_all_species()]
        class_options = [c["name"] for c in fetch_all_classes()]
        bg_options = [b["name"] for b in fetch_all_backgrounds()]
        feat_options = [f["name"] for f in fetch_all_origin_feats()]

        c1, c2 = st.columns(2)
        with c1:
            w_data["species"] = st.selectbox("Espécie 2024", species_options, index=0)
            w_data["initial_class"] = st.selectbox("Classe Inicial (Nível 1)", class_options, index=0)
        with c2:
            w_data["background"] = st.selectbox("Antecedente 2024", bg_options, index=0)
            w_data["origin_feat"] = st.selectbox("Talento de Origem 2024", feat_options, index=0)

        # Exibe prévia do Dado de Vida e PV Nível 1
        cls_name = w_data["initial_class"]
        hit_die, avg_hd = CLASS_HIT_DICE.get(cls_name, (8, 5))
        con_mod = w_data["attributes"].modifier("CON")
        lvl1_max_hp = hit_die + con_mod

        st.markdown(f"""
        <div class="grimoire-card" style="background-color: #27272A;">
            <h4>📊 Resumo do Nível 1 ({cls_name}):</h4>
            <ul>
                <li><b>Dado de Vida (Hit Die):</b> 1d{hit_die}</li>
                <li><b>Pontos de Vida Iniciais (PV Max):</b> <b>{lvl1_max_hp} PV</b> (Máximo do Dado {hit_die} + Mod CON {con_mod:+d})</li>
                <li><b>Salvaguardas Iniciais:</b> {', '.join(CLASS_SAVING_THROWS.get(cls_name, ['FOR', 'CON']))}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.button("⬅️ VOLTAR", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
        with col_nav2:
            if st.button("🔥 FINALIZAR E CRIAR PERSONAGEM", use_container_width=True):
                # Constrói o objeto Personagem final Nível 1
                init_class_info = ClassLevelInfo(
                    class_name=cls_name,
                    level=1,
                    subclass_name="",
                    hp_gained_history=[lvl1_max_hp]
                )

                # Histórico inicial de evolução por nível
                lvl1_features = get_class_features_by_level(cls_name, 1)
                now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

                initial_log = EvolutionLogEntry(
                    level=1,
                    class_name=cls_name,
                    class_level=1,
                    hp_gained=lvl1_max_hp,
                    hp_roll=hit_die,
                    features_unlocked=lvl1_features,
                    asi_or_feat=f"Talento de Origem: {w_data['origin_feat']}",
                    spell_slots_unlocked={"1": 2} if cls_name in ["Mago", "Clérigo", "Druida", "Bardo", "Feiticeiro"] else {},
                    timestamp=now_str
                )

                new_char = Character(
                    name=w_data["name"],
                    campaign=w_data["campaign"],
                    alignment=w_data["alignment"],
                    languages=w_data["languages"],
                    species=w_data["species"],
                    background=w_data["background"],
                    origin_feat=w_data["origin_feat"],
                    classes=[init_class_info],
                    attributes=w_data["attributes"],
                    max_hp=lvl1_max_hp,
                    current_hp=lvl1_max_hp,
                    saving_throw_proficiencies=CLASS_SAVING_THROWS.get(cls_name, ["FOR", "CON"]),
                    evolution_log=[initial_log],
                    created_at=now_str,
                    updated_at=now_str
                )

                new_id = save_character(new_char)
                st.success(f"Personagem '{new_char.name}' criado com sucesso!")
                on_finish(new_id)
