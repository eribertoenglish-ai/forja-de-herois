import random
import streamlit as st

def render_dice_roller_widget():
    """Renderiza o widget interativo de rolagem de dados D&D em pt-BR."""
    st.markdown("### 🎲 Rolador de Dados Interativo")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        dice_type = st.selectbox("Dado", ["d20", "d4", "d6", "d8", "d10", "d12", "d100"], index=0)
    with col2:
        num_dice = st.number_input("Qtd Dados", min_value=1, max_value=10, value=1)
    with col3:
        mod_val = st.number_input("Modificador", value=0, step=1)
        
    advantage_option = "Normal"
    if dice_type == "d20" and num_dice == 1:
        advantage_option = st.radio("Vantagem", ["Normal", "Vantagem", "Desvantagem"], horizontal=True)
        
    if st.button("🎲 ROLAR DADOS", use_container_width=True):
        sides = int(dice_type.replace("d", ""))
        
        if dice_type == "d20" and advantage_option != "Normal":
            r1 = random.randint(1, 20)
            r2 = random.randint(1, 20)
            if advantage_option == "Vantagem":
                chosen = max(r1, r2)
                detail = f"Rolagens: [{r1}, {r2}] (Maior: {chosen})"
            else:
                chosen = min(r1, r2)
                detail = f"Rolagens: [{r1}, {r2}] (Menor: {chosen})"
            total = chosen + mod_val
            st.success(f"**Resultado:** {total}  \n*{detail} + Mod({mod_val:+}d)*")
        else:
            rolls = [random.randint(1, sides) for _ in range(num_dice)]
            sum_rolls = sum(rolls)
            total = sum_rolls + mod_val
            rolls_str = ", ".join(map(str, rolls))
            st.success(f"**Resultado Final: {total}**  \n*Dados [{dice_type}]: ({rolls_str}) + Mod ({mod_val:+}d)*")
            
            if 20 in rolls and sides == 20:
                st.balloons()
                st.markdown("🔥 **SUCESSO CRÍTICO! (20 Natural)**")
            elif 1 in rolls and sides == 20:
                st.error("💀 **FALHA CRÍTICA! (1 Natural)**")
