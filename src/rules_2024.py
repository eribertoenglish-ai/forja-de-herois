import math
from typing import Dict, List, Tuple

# Bônus de Proficiência baseado no nível total do personagem (Regras 2024)
def get_proficiency_bonus(total_level: int) -> int:
    if total_level <= 4:
        return 2
    elif total_level <= 8:
        return 3
    elif total_level <= 12:
        return 4
    elif total_level <= 16:
        return 5
    else:
        return 6

# Lista Oficial de Perícias 2024 em pt-BR com seus atributos correspondentes
SKILLS_2024: Dict[str, str] = {
    "Acrobacia": "DES",
    "Adestrar Animais": "SAB",
    "Arcanismo": "INT",
    "Atletismo": "FOR",
    "Atuação": "CAR",
    "Enganação": "CAR",
    "Furtividade": "DES",
    "História": "INT",
    "Intimidação": "CAR",
    "Intuição": "SAB",
    "Investigação": "INT",
    "Medicina": "SAB",
    "Natureza": "INT",
    "Percepção": "SAB",
    "Persuasão": "CAR",
    "Prestidigitação": "DES",
    "Religião": "INT",
    "Sobrevivência": "SAB"
}

# Dados de Vida (Hit Die) e valores médios por classe
CLASS_HIT_DICE: Dict[str, Tuple[int, int]] = {
    "Bárbaro": (12, 7),
    "Guerreiro": (10, 6),
    "Paladino": (10, 6),
    "Patrulheiro": (10, 6),
    "Bardo": (8, 5),
    "Clérigo": (8, 5),
    "Druida": (8, 5),
    "Monge": (8, 5),
    "Ladino": (8, 5),
    "Bruxo": (8, 5),
    "Feiticeiro": (6, 4),
    "Mago": (6, 4),
}

# Salvaguardas primárias concedidas por classe no Nível 1
CLASS_SAVING_THROWS: Dict[str, List[str]] = {
    "Bárbaro": ["FOR", "CON"],
    "Bardo": ["DES", "CAR"],
    "Clérigo": ["SAB", "CAR"],
    "Druida": ["INT", "SAB"],
    "Feiticeiro": ["CON", "CAR"],
    "Guerreiro": ["FOR", "CON"],
    "Ladino": ["DES", "INT"],
    "Mago": ["INT", "SAB"],
    "Monge": ["FOR", "DES"],
    "Paladino": ["SAB", "CAR"],
    "Patrulheiro": ["FOR", "DES"],
    "Bruxo": ["SAB", "CAR"]
}

# Tipos de Conjuradores para Tabela Multiclasse 2024
FULL_CASTERS = ["Mago", "Clérigo", "Druida", "Bardo", "Feiticeiro"]
HALF_CASTERS = ["Paladino", "Patrulheiro"]
THIRD_CASTERS = ["Guerreiro", "Ladino"] # Válido se tiver subclasse mágica

# Tabela Multiclasse de Espaços de Magia por Nível Efetivo de Conjurador (1 a 20)
# Nível Efetivo -> {Nível da Magia (1-9): Quantidade de Slots}
MULTICLASS_SPELL_SLOTS_TABLE: Dict[int, Dict[int, int]] = {
    1: {1: 2},
    2: {1: 3},
    3: {1: 4, 2: 2},
    4: {1: 4, 2: 3},
    5: {1: 4, 2: 3, 3: 2},
    6: {1: 4, 2: 3, 3: 3},
    7: {1: 4, 2: 3, 3: 3, 4: 1},
    8: {1: 4, 2: 3, 3: 3, 4: 2},
    9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}

# Tabela Especial de Magia de Pacto (Bruxo 2024)
WARLOCK_SPELL_SLOTS: Dict[int, Tuple[int, int]] = {
    # Nível do Bruxo -> (Quantidade de Slots, Nível dos Slots)
    1: (1, 1), 2: (2, 1), 3: (2, 2), 4: (2, 2), 5: (2, 3),
    6: (2, 3), 7: (2, 4), 8: (2, 4), 9: (2, 5), 10: (2, 5),
    11: (3, 5), 12: (3, 5), 13: (3, 5), 14: (3, 5), 15: (3, 5),
    16: (3, 5), 17: (4, 5), 18: (4, 5), 19: (4, 5), 20: (4, 5)
}

def calculate_multiclass_spell_slots(classes_list: List[Dict[str, any]]) -> Dict[int, int]:
    """
    Calcula os espaços de magia máximos por nível (1 a 9) com base na combinação de classes e níveis 2024.
    """
    effective_caster_level = 0
    warlock_level = 0

    for c in classes_list:
        c_name = c.get("class_name", "")
        lvl = c.get("level", 1)
        sub = c.get("subclass_name", "").lower()

        if c_name == "Bruxo":
            warlock_level += lvl
        elif c_name in FULL_CASTERS:
            effective_caster_level += lvl
        elif c_name in HALF_CASTERS:
            # Nas Regras 2024, meio-conjuradores arredondam para cima (math.ceil(lvl / 2))
            effective_caster_level += math.ceil(lvl / 2)
        elif c_name in THIRD_CASTERS:
            # Se possui subclasse mágica como Cavaleiro Místico ou Trapaceiro Arcano
            if any(term in sub for term in ["místico", "mistico", "arcano"]):
                effective_caster_level += math.ceil(lvl / 3)

    slots: Dict[int, int] = {lvl: 0 for lvl in range(1, 10)}

    # Preenche slots de conjurador regular se houver nível efetivo
    if effective_caster_level > 0:
        eff_lvl = min(effective_caster_level, 20)
        base_slots = MULTICLASS_SPELL_SLOTS_TABLE.get(eff_lvl, {})
        for spell_lvl, count in base_slots.items():
            slots[spell_lvl] += count

    # Adiciona slots de Pacto do Bruxo se houver
    if warlock_level > 0:
        w_slots, w_lvl = WARLOCK_SPELL_SLOTS.get(min(warlock_level, 20), (0, 0))
        if w_lvl in slots:
            slots[w_lvl] += w_slots

    return slots

def get_class_features_by_level(class_name: str, level: int, subclass_name: str = "") -> List[str]:
    """
    Retorna os recursos de classe desbloqueados em pt-BR em um determinado nível de classe (1-20).
    """
    features_map: Dict[str, Dict[int, List[str]]] = {
        "Guerreiro": {
            1: ["Retomada de Fôlego (Second Wind)", "Estilo de Luta"],
            2: ["Surto de Ação (Action Surge)", "Tática de Combate"],
            3: ["Subclasse de Guerreiro", "Maestria em Armas"],
            4: ["Incremento de Atributo ou Talento"],
            5: ["Ataque Extra"],
            6: ["Incremento de Atributo ou Talento"],
            7: ["Recurso de Subclasse (Nível 7)"],
            8: ["Incremento de Atributo ou Talento"],
            9: ["Indomável (Indomitable)"],
            10: ["Recurso de Subclasse (Nível 10)"],
            11: ["Ataque Extra (2)"],
            12: ["Incremento de Atributo ou Talento"],
            13: ["Indomável (2 usos)"],
            14: ["Incremento de Atributo ou Talento"],
            15: ["Recurso de Subclasse (Nível 15)"],
            16: ["Incremento de Atributo ou Talento"],
            17: ["Surto de Ação (2 usos)", "Indomável (3 usos)"],
            18: ["Recurso de Subclasse (Nível 18)"],
            19: ["Incremento de Atributo ou Talento"],
            20: ["Épico da Guerra (Ataque Extra 3)"]
        },
        "Mago": {
            1: ["Conjuração", "Livro de Magias", "Recuperação Arcana"],
            2: ["Subclasse de Mago (Escola de Magia)"],
            3: ["Magias de Nível 2"],
            4: ["Incremento de Atributo ou Talento"],
            5: ["Magias de Nível 3"],
            6: ["Recurso de Subclasse (Nível 6)"],
            7: ["Magias de Nível 4"],
            8: ["Incremento de Atributo ou Talento"],
            9: ["Magias de Nível 5"],
            10: ["Recurso de Subclasse (Nível 10)"],
            11: ["Magias de Nível 6"],
            12: ["Incremento de Atributo ou Talento"],
            13: ["Magias de Nível 7"],
            14: ["Recurso de Subclasse (Nível 14)"],
            15: ["Magias de Nível 8"],
            16: ["Incremento de Atributo ou Talento"],
            17: ["Magias de Nível 9"],
            18: ["Dominância Mágica"],
            19: ["Incremento de Atributo ou Talento"],
            20: ["Magias de Assinatura"]
        },
        "Clérigo": {
            1: ["Conjuração", "Domínio Divino (Subclasse)", "Canalizar Divindade"],
            2: ["Recurso de Canalizar Divindade"],
            3: ["Magias Divinas de Nível 2"],
            4: ["Incremento de Atributo ou Talento"],
            5: ["Destruir Mortos-Vivos", "Magias de Nível 3"],
            6: ["Recurso de Subclasse"],
            7: ["Magias de Nível 4"],
            8: ["Incremento de Atributo ou Talento", "Golpe Divino / Conjurador Potente"],
            9: ["Magias de Nível 5"],
            10: ["Intervenção Divina"],
            11: ["Magias de Nível 6"],
            12: ["Incremento de Atributo ou Talento"],
            13: ["Magias de Nível 7"],
            14: ["Destruir Mortos-Vivos Aprimorado"],
            15: ["Magias de Nível 8"],
            16: ["Incremento de Atributo ou Talento"],
            17: ["Recurso de Subclasse (Nível 17)", "Magias de Nível 9"],
            18: ["Canalizar Divindade (3 usos)"],
            19: ["Incremento de Atributo ou Talento"],
            20: ["Intervenção Divina Garantida"]
        },
        "Ladino": {
            1: ["Ataque Furtivo (1d6)", "Especialidade", "Gíria de Ladrão"],
            2: ["Ação Astuta"],
            3: ["Subclasse de Ladino (Arquétipo)", "Ataque Furtivo (2d6)"],
            4: ["Incremento de Atributo ou Talento"],
            5: ["Esquiva Sobrenatural", "Ataque Furtivo (3d6)"],
            6: ["Especialidade Adicional"],
            7: ["Evasão", "Ataque Furtivo (4d6)"],
            8: ["Incremento de Atributo ou Talento"],
            9: ["Recurso de Subclasse", "Ataque Furtivo (5d6)"],
            10: ["Incremento de Atributo ou Talento"],
            11: ["Talento Confiável", "Ataque Furtivo (6d6)"],
            12: ["Incremento de Atributo ou Talento"],
            13: ["Recurso de Subclasse", "Ataque Furtivo (7d6)"],
            14: ["Sentido de Sombras"],
            15: ["Mente Escorregadia", "Ataque Furtivo (8d6)"],
            16: ["Incremento de Atributo ou Talento"],
            17: ["Recurso de Subclasse", "Ataque Furtivo (9d6)"],
            18: ["Elusivo"],
            19: ["Incremento de Atributo ou Talento"],
            20: ["Golpe de Sorte", "Ataque Furtivo (10d6)"]
        },
        "Bárbaro": {
            1: ["Fúria", "Defesa Sem Armadura"],
            2: ["Ataque Temerário", "Sentido de Perigo"],
            3: ["Subclasse de Bárbaro (Caminho)"],
            4: ["Incremento de Atributo ou Talento"],
            5: ["Ataque Extra", "Movimento Rápido"],
            6: ["Recurso de Subclasse"],
            7: ["Instinto Selvagem"],
            8: ["Incremento de Atributo ou Talento"],
            9: ["Crítico Brutal (1 dado)"],
            10: ["Recurso de Subclasse"],
            11: ["Fúria Implacável"],
            12: ["Incremento de Atributo ou Talento"],
            13: ["Crítico Brutal (2 dados)"],
            14: ["Recurso de Subclasse"],
            15: ["Fúria Persistente"],
            16: ["Incremento de Atributo ou Talento"],
            17: ["Crítico Brutal (3 dados)"],
            18: ["Força Indômita"],
            19: ["Incremento de Atributo ou Talento"],
            20: ["Campeão Primal (FOR e CON +4)"]
        }
    }

    base_features = features_map.get(class_name, {}).get(level, [f"Habilidade de {class_name} Nível {level}"])
    if subclass_name and level in [3, 6, 7, 10, 14, 15, 17, 18]:
        base_features.append(f"Aprimoramento de Subclasse: {subclass_name}")
    return base_features
