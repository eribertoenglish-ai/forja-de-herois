import json
import base64
import datetime
import streamlit as st
from PIL import Image
import io

from src.models import Character, ClassLevelInfo, EvolutionLogEntry
from src.database import save_character, fetch_all_spells, fetch_all_equipment, fetch_all_classes
from src.rules_2024 import (
    get_proficiency_bonus, SKILLS_2024, CLASS_HIT_DICE,
    calculate_multiclass_spell_slots, get_class_features_by_level
)
from src.pdf_export import generate_character_pdf
from src.ui.dice_roller import render_dice_roller_widget

def render_character_sheet(char: Character, on_back_to_dashboard):
    """Renderiza a ficha interativa detalhada do personagem em pt-BR."""

    # ----------------------------------------------------
    # CABEÇALHO SUPERIOR & AVATAR
    # ----------------------------------------------------
    col_hdr1, col_hdr2, col_hdr3 = st.columns([1, 3, 2])

    with col_hdr1:
        # Exibe ou permite upload do Avatar (base64)
        if char.avatar_b64:
            try:
                img_data = base64.b64decode(char.avatar_b64)
                st.image(img_data, width=110)
            except Exception:
                st.image("https://via.placeholder.com/110?text=Avatar", width=110)
        else:
            st.markdown("🖼️ *Sem Avatar*")

        up_file = st.file_uploader("Upload Foto", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if up_file is not None:
            raw = up_file.read()
            char.avatar_b64 = base64.b64encode(raw).decode("utf-8")
            save_character(char)
            st.rerun()

    with col_hdr2:
        st.markdown(f"# 🛡️ {char.name}")
        prof_bonus = get_proficiency_bonus(char.total_level)
        classes_fmt = " / ".join([f"{c.class_name} {c.level}" for c in char.classes]) if char.classes else "Sem Classe"
        st.markdown(f"##### **Nível Total {char.total_level}** | {classes_fmt}")
        st.markdown(f"**Espécie:** {char.species} | **Antecedente:** {char.background} | **Campanha:** {char.campaign or 'Padrão'}")

    with col_hdr3:
        if st.button("⬅️ VOLTAR AO PAINEL", use_container_width=True):
            on_back_to_dashboard()

        # Botão de Exportação para PDF
        pdf_bytes = generate_character_pdf(char)
        st.download_button(
            label="📄 EXPORTAR PARA PDF (PT-BR)",
            data=pdf_bytes,
            file_name=f"ficha_{char.name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.markdown(f"<div style='text-align: right;'><span class='badge-gold'>Bônus Proficiência: +{prof_bonus}</span></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ----------------------------------------------------
    # ENGINE DE EVOLUÇÃO DE NÍVEL & MULTICLASSE (BARRINHA)
    # ----------------------------------------------------
    with st.expander("⚡ SUBIR DE NÍVEL / EVOLUIR PERSONAGEM (REGRAS 2024)", expanded=False):
        st.markdown("#### Evoluir ou Adicionar Nova Classe")
        existing_class_names = [c.class_name for c in char.classes]
        all_classes_db = [c["name"] for c in fetch_all_classes()]

        c_evo1, c_evo2, c_evo3 = st.columns(3)
        with c_evo1:
            target_class_name = st.selectbox("Escolha a Classe para Evoluir", all_classes_db, index=0)
        with c_evo2:
            hit_die, avg_hd = CLASS_HIT_DICE.get(target_class_name, (8, 5))
            con_mod = char.attributes.modifier("CON")
            default_hp = max(1, avg_hd + con_mod)

            hp_roll_mode = st.radio("Modo de Vida no Nível", ["Média Automática", "Rolar / Digitar Valor Manual"], horizontal=True)
            if hp_roll_mode == "Média Automática":
                rolled_val = avg_hd
            else:
                rolled_val = st.number_input(f"Resultado do Dado (1d{hit_die})", min_value=1, max_value=hit_die, value=avg_hd)

            total_gained_hp = max(1, rolled_val + con_mod)
            st.caption(f"PV Ganho no Nível: **+{total_gained_hp}** ({rolled_val} no dado + CON {con_mod:+d})")

        with c_evo3:
            asi_or_feat_input = st.text_input("Incremento de Atributo ou Talento", value="")
            subclass_input = st.text_input("Subclasse (se aplicável)", value="")

        if st.button("🚀 CONFIRMAR E REGISTRAR NÍVEL", use_container_width=True):
            # 1. Atualiza ou Adiciona a Classe no Objeto
            found_class = None
            for c in char.classes:
                if c.class_name == target_class_name:
                    found_class = c
                    break

            if found_class:
                found_class.level += 1
                new_class_lvl = found_class.level
                found_class.hp_gained_history.append(total_gained_hp)
                if subclass_input:
                    found_class.subclass_name = subclass_input
            else:
                new_class_lvl = 1
                char.classes.append(ClassLevelInfo(
                    class_name=target_class_name,
                    level=1,
                    subclass_name=subclass_input,
                    hp_gained_history=[total_gained_hp]
                ))

            # 2. Atualiza Vida Máxima
            char.max_hp += total_gained_hp
            char.current_hp += total_gained_hp

            # 3. Registra Entrada Imutável no Histórico de Evolução
            unlocked_features = get_class_features_by_level(target_class_name, new_class_lvl, subclass_input)
            now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

            evo_entry = EvolutionLogEntry(
                level=char.total_level,
                class_name=target_class_name,
                class_level=new_class_lvl,
                hp_gained=total_gained_hp,
                hp_roll=rolled_val,
                features_unlocked=unlocked_features,
                asi_or_feat=asi_or_feat_input,
                spell_slots_unlocked={},
                timestamp=now_str
            )
            char.evolution_log.append(evo_entry)

            save_character(char)
            st.toast(f"Nível {char.total_level} alcançado em {target_class_name}!")
            st.rerun()

    # ----------------------------------------------------
    # ABAS DA FICHA DE PERSONAGEM
    # ----------------------------------------------------
    tab_overview, tab_combat, tab_spells, tab_inventory, tab_evolution = st.tabs([
        "📋 VISÃO GERAL & ATRIBUTOS",
        "⚔️ COMBATE & DADOS",
        "🔮 CONJURAÇÃO DE MAGIAS",
        "🎒 INVENTÁRIO",
        "📜 FICHA DE EVOLUÇÃO POR NÍVEL"
    ])

    # ----------------------------------------------------
    # ABA 1: VISÃO GERAL & ATRIBUTOS
    # ----------------------------------------------------
    with tab_overview:
        st.markdown("### 📊 Atributos Principais & Perícias (2024)")

        # 6 Atributos
        attrs = char.attributes
        c1, c2, c3, c4, c5, c6 = st.columns(6)

        def render_attr_box(col, name, attr_val):
            with col:
                mod = attrs.modifier(name)
                st.markdown(f"""
                <div class="grimoire-card" style="text-align: center; padding: 10px;">
                    <h4 style="margin: 0; color: #D97706;">{name}</h4>
                    <h2 style="margin: 4px 0; color: #FFFFFF;">{attr_val}</h2>
                    <span class="badge-gold">{mod:+d}</span>
                </div>
                """, unsafe_allow_html=True)
                new_val = st.number_input(f"Edit {name}", min_value=1, max_value=30, value=attr_val, key=f"edit_{name}", label_visibility="collapsed")
                setattr(attrs, name, new_val)

        render_attr_box(c1, "FOR", attrs.FOR)
        render_attr_box(c2, "DES", attrs.DES)
        render_attr_box(c3, "CON", attrs.CON)
        render_attr_box(c4, "INT", attrs.INT)
        render_attr_box(c5, "SAB", attrs.SAB)
        render_attr_box(c6, "CAR", attrs.CAR)

        st.markdown("<br/>", unsafe_allow_html=True)
        col_sec1, col_sec2 = st.columns([1, 2])

        with col_sec1:
            st.markdown("#### 🛡️ Salvaguardas / Testes de Resistência")
            for save_code in ["FOR", "DES", "CON", "INT", "SAB", "CAR"]:
                mod = attrs.modifier(save_code)
                is_prof = save_code in char.saving_throw_proficiencies
                if is_prof:
                    mod += prof_bonus

                checked = st.checkbox(f"**{save_code}** (Bônus: {mod:+d})", value=is_prof, key=f"save_{save_code}")
                if checked and save_code not in char.saving_throw_proficiencies:
                    char.saving_throw_proficiencies.append(save_code)
                elif not checked and save_code in char.saving_throw_proficiencies:
                    char.saving_throw_proficiencies.remove(save_code)

        with col_sec2:
            st.markdown("#### 🎯 18 Perícias Oficiais (D&D 5e 2024)")
            st.caption("Selecione: **0 = Nenhuma**, **1 = Proficiente**, **2 = Especialidade (Expertise)**")

            sc1, sc2 = st.columns(2)
            skill_items = list(SKILLS_2024.items())
            half = len(skill_items) // 2

            def render_skill_controls(container, items):
                for skill_name, attr_code in items:
                    prof_lvl = char.skill_proficiencies.get(skill_name, 0)
                    total_mod = attrs.modifier(attr_code) + (prof_bonus * prof_lvl)

                    icol1, icol2 = container.columns([3, 2])
                    with icol1:
                        st.markdown(f"**{skill_name}** ({attr_code}): **{total_mod:+d}**")
                    with icol2:
                        new_prof = st.selectbox(
                            f"Prof {skill_name}",
                            options=[0, 1, 2],
                            index=prof_lvl,
                            format_func=lambda x: "⚪ Nenhuma" if x==0 else ("🟡 Proficiente" if x==1 else "⭐ Especialidade"),
                            key=f"sk_{skill_name}",
                            label_visibility="collapsed"
                        )
                        char.skill_proficiencies[skill_name] = new_prof

            render_skill_controls(sc1, skill_items[:half])
            render_skill_controls(sc2, skill_items[half:])

    # ----------------------------------------------------
    # ABA 2: COMBATE & DADOS
    # ----------------------------------------------------
    with tab_combat:
        st.markdown("### ⚔️ Status de Combate & Vitalidade")

        c_v1, c_v2, c_v3, c_v4 = st.columns(4)
        with c_v1:
            des_mod = attrs.modifier("DES")
            calc_ca = 10 + des_mod
            st.metric("Classe de Armadura (CA)", f"{char.armor_class_override if char.armor_class_override else calc_ca}")
            override_ca = st.number_input("Override CA", value=char.armor_class_override or 0)
            char.armor_class_override = override_ca if override_ca > 0 else None
        with c_v2:
            st.metric("Pontos de Vida (PV)", f"{char.current_hp} / {char.max_hp}")
            new_curr_hp = st.number_input("PV Atual", min_value=0, max_value=500, value=char.current_hp)
            char.current_hp = new_curr_hp
        with c_v3:
            st.metric("Iniciativa", f"{des_mod:+d}")
            new_temp_hp = st.number_input("PV Temporários", min_value=0, max_value=200, value=char.temp_hp)
            char.temp_hp = new_temp_hp
        with c_v4:
            st.metric("Deslocamento", f"{char.speed}m")
            if st.button("💖 DESCANSO LONGO (RESTAURAR PV)", use_container_width=True):
                char.current_hp = char.max_hp
                char.used_spell_slots = {}
                save_character(char)
                st.success("Pontos de Vida e Espaços de Magia restaurados!")
                st.rerun()

        st.markdown("---")
        # Widget do Rolador de Dados
        render_dice_roller_widget()

    # ----------------------------------------------------
    # ABA 3: CONJURAÇÃO DE MAGIAS
    # ----------------------------------------------------
    with tab_spells:
        st.markdown("### 🔮 Gerenciador de Magias & Espaços (Multiclasse 2024)")

        # Calcula slots totais por regras 2024
        classes_dicts = [c.to_dict() for c in char.classes]
        max_slots = calculate_multiclass_spell_slots(classes_dicts)

        st.markdown("#### ⚡ Espaços de Magia Disponíveis (Slots)")
        slot_cols = st.columns(9)
        for spell_lvl in range(1, 10):
            with slot_cols[spell_lvl - 1]:
                m_slot = max_slots.get(spell_lvl, 0)
                used = char.used_spell_slots.get(str(spell_lvl), 0)
                avail = max(0, m_slot - used)

                st.markdown(f"**Nível {spell_lvl}**")
                st.markdown(f"### {avail} / {m_slot}")
                if m_slot > 0:
                    if st.button("Gastar 1", key=f"spend_slot_{spell_lvl}"):
                        if avail > 0:
                            char.used_spell_slots[str(spell_lvl)] = used + 1
                            save_character(char)
                            st.rerun()

        st.markdown("---")
        st.markdown("#### 📚 Biblioteca & Magias Conhecidas (pt-BR)")

        all_spells_db = fetch_all_spells()
        spell_names = [s["name"] for s in all_spells_db]
        selected_spell_to_add = st.selectbox("Adicionar Magia do Grimório", spell_names)
        if st.button("➕ Adicionar Magia"):
            if not any(s.get("name") == selected_spell_to_add for s in char.spells):
                spell_obj = next((s for s in all_spells_db if s["name"] == selected_spell_to_add), None)
                if spell_obj:
                    char.spells.append(spell_obj)
                    save_character(char)
                    st.success(f"Magia '{selected_spell_to_add}' adicionada!")
                    st.rerun()

        if char.spells:
            for idx, sp in enumerate(char.spells):
                with st.expander(f"✨ Nível {sp.get('level', 0)} - {sp.get('name')} ({sp.get('school', 'Magia')})"):
                    st.write(f"**Tempo de Conjuração:** {sp.get('casting_time')} | **Alcance:** {sp.get('range_area')}")
                    st.write(f"**Componentes:** {sp.get('components')} | **Duração:** {sp.get('duration')}")
                    st.write(sp.get("description", ""))
                    if st.button(f"🗑️ Remover Magia", key=f"rem_sp_{idx}"):
                        char.spells.pop(idx)
                        save_character(char)
                        st.rerun()
        else:
            st.info("Nenhuma magia adicionada à ficha ainda.")

    # ----------------------------------------------------
    # ABA 4: INVENTÁRIO & EQUIPAMENTOS
    # ----------------------------------------------------
    with tab_inventory:
        st.markdown("### 🎒 Inventário & Riqueza")

        # Moedas
        st.markdown("#### 🪙 Moedas (Peças)")
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        with mc1: char.gold = st.number_input("Ouro (PO)", min_value=0, value=char.gold)
        with mc2: char.silver = st.number_input("Prata (PP)", min_value=0, value=char.silver)
        with mc3: char.copper = st.number_input("Cobre (PC)", min_value=0, value=char.copper)
        with mc4: char.electrum = st.number_input("Electrum (PE)", min_value=0, value=char.electrum)
        with mc5: char.platinum = st.number_input("Platina (PL)", min_value=0, value=char.platinum)

        st.markdown("---")
        st.markdown("#### 🗡️ Adicionar Equipamentos da Lista Oficial")
        all_eq_db = fetch_all_equipment()
        eq_names = [e["name"] for e in all_eq_db]
        selected_eq = st.selectbox("Selecione um Equipamento", eq_names)
        if st.button("➕ Adicionar ao Inventário"):
            eq_obj = next((e for e in all_eq_db if e["name"] == selected_eq), None)
            if eq_obj:
                char.inventory.append(eq_obj)
                save_character(char)
                st.success(f"'{selected_eq}' adicionado ao inventário!")
                st.rerun()

        if char.inventory:
            for idx, item in enumerate(char.inventory):
                st.markdown(f"• **{item.get('name')}** ({item.get('type', 'Item')}) - *Dano/CA: {item.get('damage', '-')}* | {item.get('properties', '')}")
        else:
            st.info("Inventário vazio.")

    # ----------------------------------------------------
    # ABA 5: RESUMO DE EVOLUÇÃO DO PERSONAGEM (TIMELINE)
    # ----------------------------------------------------
    with tab_evolution:
        st.markdown("### 📜 FICHA DE EVOLUÇÃO POR NÍVEL (HISTÓRICO IMUTÁVEL)")
        st.markdown("##### *Registro detalhado de cada nível alcançado no desenvolvimento do herói.*")
        st.markdown("---")

        if not char.evolution_log:
            st.info("Nenhum registro no histórico de evolução ainda.")
        else:
            for entry in char.evolution_log:
                st.markdown(f"""
                <div class="grimoire-card">
                    <div style="display: flex; justify-content: space-between;">
                        <h4 style="margin: 0; color: #D97706;">⚡ Nível {entry.level} Total — {entry.class_name} (Nível de Classe {entry.class_level})</h4>
                        <span class="badge-dark">{entry.timestamp}</span>
                    </div>
                    <p style="margin-top: 8px; color: #10B981;">
                        <b>❤️ Vida Ganha no Nível:</b> +{entry.hp_gained} PV (Dado Rolado/Média: {entry.hp_roll} + Mod CON)
                    </p>
                    <p style="color: #FBBF24;">
                        <b>✨ Recursos de Classe Unlocked:</b> {', '.join(entry.features_unlocked) if entry.features_unlocked else 'Nenhum'}
                    </p>
                    <p style="color: #E4E4E7;">
                        <b>🎯 Incremento / Talento Escolhido:</b> {entry.asi_or_feat or 'Nenhum'}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # Salva alterações no final de cada renderização de aba
    save_character(char)
