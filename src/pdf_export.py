import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from src.models import Character
from src.rules_2024 import get_proficiency_bonus, SKILLS_2024

def generate_character_pdf(character: Character) -> bytes:
    """
    Gera um documento PDF limpo e imprimível em folha A4 com a ficha completa do personagem em pt-BR.
    Retorna os bytes do arquivo PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    story = []
    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#D97706"),
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#4B5563")
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#92400E"),
        spaceBefore=10,
        spaceAfter=4
    )
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11
    )
    bold_style = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11
    )

    # 1. Cabeçalho Principal
    story.append(Paragraph(f"FORJA DE HERÓIS — FICHA DE PERSONAGEM (D&D 5e 2024)", subtitle_style))
    story.append(Paragraph(character.name.upper(), title_style))
    story.append(Spacer(1, 4))

    # Tabela com Informações Básicas
    prof_bonus = get_proficiency_bonus(character.total_level)
    classes_str = " / ".join([f"{c.class_name} Nível {c.level}" for c in character.classes]) if character.classes else "Sem Classe"

    header_data = [
        [
            Paragraph(f"<b>Espécie:</b> {character.species}", normal_style),
            Paragraph(f"<b>Antecedente:</b> {character.background}", normal_style),
            Paragraph(f"<b>Talento de Origem:</b> {character.origin_feat or 'Nenhum'}", normal_style)
        ],
        [
            Paragraph(f"<b>Classe(s):</b> {classes_str}", normal_style),
            Paragraph(f"<b>Nível Total:</b> {character.total_level}", normal_style),
            Paragraph(f"<b>Bônus Proficiência:</b> +{prof_bonus}", normal_style)
        ],
        [
            Paragraph(f"<b>Campanha:</b> {character.campaign or 'Geral'}", normal_style),
            Paragraph(f"<b>Tendência:</b> {character.alignment}", normal_style),
            Paragraph(f"<b>Idiomas:</b> {character.languages}", normal_style)
        ]
    ]

    header_table = Table(header_data, colWidths=[180, 180, 175])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D97706")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # 2. Atributos Principais e Status de Combate
    story.append(Paragraph("ATRIBUTOS & STATUS DE COMBATE", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D97706"), spaceAfter=6))

    attrs = character.attributes
    attr_headers = ["FOR", "DES", "CON", "INT", "SAB", "CAR"]
    attr_vals = [attrs.FOR, attrs.DES, attrs.CON, attrs.INT, attrs.SAB, attrs.CAR]
    attr_mods = [f"{attrs.modifier(a):+d}" for a in attr_headers]

    attr_data = [
        [Paragraph(f"<b>{h}</b>", bold_style) for h in attr_headers],
        [Paragraph(f"<font size=12><b>{v}</b></font>", normal_style) for v in attr_vals],
        [Paragraph(f"Mod: <b>{m}</b>", bold_style) for m in attr_mods]
    ]

    attr_table = Table(attr_data, colWidths=[88]*6)
    attr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F59E0B")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FCD34D")),
        ('PADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(attr_table)
    story.append(Spacer(1, 8))

    # Status de Combate (CA, PV, Iniciativa, Deslocamento)
    des_mod = attrs.modifier("DES")
    ca_val = character.armor_class_override if character.armor_class_override is not None else (10 + des_mod)
    init_val = f"{des_mod:+d}"

    vitals_data = [
        [
            Paragraph("<b>Classe de Armadura (CA)</b>", bold_style),
            Paragraph("<b>Pontos de Vida (PV Max)</b>", bold_style),
            Paragraph("<b>Iniciativa</b>", bold_style),
            Paragraph("<b>Deslocamento</b>", bold_style)
        ],
        [
            Paragraph(f"<font size=14><b>{ca_val}</b></font>", normal_style),
            Paragraph(f"<font size=14><b>{character.max_hp}</b></font>", normal_style),
            Paragraph(f"<font size=14><b>{init_val}</b></font>", normal_style),
            Paragraph(f"<font size=14><b>{character.speed}m</b></font>", normal_style)
        ]
    ]

    vitals_table = Table(vitals_data, colWidths=[133]*4)
    vitals_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FDE68A")),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    story.append(vitals_table)
    story.append(Spacer(1, 10))

    # 3. Salvaguardas e 18 Perícias Oficiais 2024
    story.append(Paragraph("SALVAGUARDAS & PERÍCIAS (2024)", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D97706"), spaceAfter=6))

    # Salvaguardas
    saves_list = []
    for code in ["FOR", "DES", "CON", "INT", "SAB", "CAR"]:
        mod = attrs.modifier(code)
        if code in character.saving_throw_proficiencies:
            mod += prof_bonus
            saves_list.append(f"<b>[X] {code}:</b> {mod:+d}")
        else:
            saves_list.append(f"[  ] {code}: {mod:+d}")

    story.append(Paragraph("<b>Testes de Resistência (Salvaguardas):</b> " + " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(saves_list), normal_style))
    story.append(Spacer(1, 6))

    # Tabela de Perícias em 2 Colunas
    skill_items = list(SKILLS_2024.items())
    half = (len(skill_items) + 1) // 2
    col1 = skill_items[:half]
    col2 = skill_items[half:]

    skill_rows = []
    for i in range(half):
        # Coluna 1
        name1, attr1 = col1[i]
        prof_lvl1 = character.skill_proficiencies.get(name1, 0)
        mod1 = attrs.modifier(attr1) + (prof_bonus * prof_lvl1)
        tag1 = "[EX]" if prof_lvl1 == 2 else ("[X] " if prof_lvl1 == 1 else "[  ]")
        cell1 = f"{tag1} <b>{name1}</b> ({attr1}): <b>{mod1:+d}</b>"

        # Coluna 2
        if i < len(col2):
            name2, attr2 = col2[i]
            prof_lvl2 = character.skill_proficiencies.get(name2, 0)
            mod2 = attrs.modifier(attr2) + (prof_bonus * prof_lvl2)
            tag2 = "[EX]" if prof_lvl2 == 2 else ("[X] " if prof_lvl2 == 1 else "[  ]")
            cell2 = f"{tag2} <b>{name2}</b> ({attr2}): <b>{mod2:+d}</b>"
        else:
            cell2 = ""

        skill_rows.append([Paragraph(cell1, normal_style), Paragraph(cell2, normal_style)])

    skills_table = Table(skill_rows, colWidths=[265, 265])
    skills_table.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB"))
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 10))

    # 4. Equipamentos e Magias
    story.append(Paragraph("EQUIPAMENTOS & INVENTÁRIO", section_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D97706"), spaceAfter=4))
    
    if character.inventory:
        inv_text = ", ".join([f"{item.get('name', 'Item')} (x{item.get('quantity', 1)})" for item in character.inventory])
    else:
        inv_text = "Nenhum equipamento registrado."
    
    money_text = f"<b>PO:</b> {character.gold} | <b>PP:</b> {character.silver} | <b>PC:</b> {character.copper}"
    story.append(Paragraph(f"{inv_text}<br/>{money_text}", normal_style))
    story.append(Spacer(1, 10))

    # 5. Histórico de Evolução
    if character.evolution_log:
        story.append(Paragraph("HISTÓRICO DE EVOLUÇÃO POR NÍVEL (TIMELINE)", section_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D97706"), spaceAfter=4))
        
        log_rows = [["Nível", "Classe Efetiva", "PV Ganho", "Recursos Unlocked / Talentos"]]
        for entry in character.evolution_log:
            feats_str = ", ".join(entry.features_unlocked) if entry.features_unlocked else "Evolução Normal"
            if entry.asi_or_feat:
                feats_str += f" | {entry.asi_or_feat}"
            log_rows.append([
                str(entry.level),
                f"{entry.class_name} ({entry.class_level})",
                f"+{entry.hp_gained} PV",
                feats_str
            ])
        
        log_table = Table(log_rows, colWidths=[40, 100, 70, 320])
        log_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D97706")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('PADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FCD34D")),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        story.append(log_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
