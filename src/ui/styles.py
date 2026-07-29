import streamlit as st

def apply_grimoire_theme():
    """Aplica o tema visual Dark Fantasy / Grimoire no Streamlit com fundo #121214 e detalhes dourados #D97706."""
    st.markdown("""
    <style>
    /* Estilo Geral da Aplicação */
    .stApp {
        background-color: #121214 !important;
        color: #E4E4E7 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Fontes e Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #D97706 !important;
        font-family: 'Georgia', serif;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Cartões e Painéis de Grimoire */
    .grimoire-card {
        background-color: #1E1E24;
        border: 1px solid #3F3F46;
        border-top: 3px solid #D97706;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .grimoire-card:hover {
        border-color: #F59E0B;
        transform: translateY(-2px);
    }
    
    /* Badges e Rotulos */
    .badge-gold {
        background-color: rgba(217, 119, 6, 0.2);
        color: #FBBF24;
        border: 1px solid #D97706;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-dark {
        background-color: #27272A;
        color: #A1A1AA;
        border: 1px solid #3F3F46;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Botões Customizados */
    .stButton > button {
        background: linear-gradient(180deg, #D97706 0%, #B45309 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #F59E0B !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(180deg, #F59E0B 0%, #D97706 100%) !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.4) !important;
    }
    
    /* Caixas de Entrada */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #18181B !important;
        border-color: #3F3F46 !important;
        color: #F4F4F5 !important;
    }

    /* Tabelas */
    .stTable {
        background-color: #1E1E24 !important;
        border-radius: 8px !important;
    }
    
    /* Rolador de Dados */
    .dice-btn {
        background-color: #27272A;
        border: 1px solid #D97706;
        color: #FBBF24;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
