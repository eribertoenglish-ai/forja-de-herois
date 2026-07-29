import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from src.models import Character

DB_PATH = "dnd2024_data.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados SQLite e insere dados padrão em pt-BR se vazias."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de Personagens
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            campaign TEXT,
            species TEXT,
            data_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabelas de Dados do Livro de Regras (D&D 2024 em pt-BR)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS species (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            speed INTEGER DEFAULT 9,
            size TEXT DEFAULT 'Médio',
            traits_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            hit_die INTEGER NOT NULL,
            primary_ability TEXT,
            saving_throws TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backgrounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            origin_feat TEXT,
            ability_boosts TEXT,
            skill_proficiencies TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS origin_feats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT DEFAULT 'Origem',
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            level INTEGER NOT NULL,
            school TEXT,
            casting_time TEXT,
            range_area TEXT,
            components TEXT,
            duration TEXT,
            classes_json TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT,
            cost TEXT,
            weight REAL,
            damage TEXT,
            damage_type TEXT,
            properties TEXT,
            description TEXT
        )
    """)

    conn.commit()

    # Popula com sementes 2024 pt-BR se estiverem vazias
    _seed_initial_data(cursor, conn)
    conn.close()

def _seed_initial_data(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    # Espécies 2024 em pt-BR
    cursor.execute("SELECT COUNT(*) FROM species")
    if cursor.fetchone()[0] == 0:
        species_list = [
            ("Humano", "Versáteis e determinados, adaptam-se a qualquer ambiente e profissão.", 9, "Médio", json.dumps(["Recurso Versátil", "Talento de Origem Extra", "Inspirador"])),
            ("Elfo", "Seres graciosos com ancestralidade mágica, visão no escuro e transe meditativo.", 9, "Médio", json.dumps(["Visão no Escuro (18m)", "Ancestralidade Feérica", "Sentidos Aguçados", "Transe"])),
            ("Anão", "Resistentes e fortes, mestres do trabalho em pedra e perigos subterrâneos.", 9, "Médio", json.dumps(["Visão no Escuro (18m)", "Resiliência Anã", "Tenacidade Anã (+1 PV/nível)"])),
            ("Halfling", "Pequenos e extremamente sortudos, habilidosos em escapar do perigo.", 8, "Pequeno", json.dumps(["Sorte Halfling", "Corajoso", "Agilidade Halfling"])),
            ("Orque", "Guerreiros natos dotados de força impressionante e determinação implacável.", 9, "Médio", json.dumps(["Visão no Escuro (18m)", "Corrida Adrenada", "Resistência Relutante"])),
            ("Draconato", "Orgulhosos descendentes de dragões com sopro elemental devastador.", 9, "Médio", json.dumps(["Ancestral Arcano Dragão", "Arma de Sopro", "Resistência Elemental", "Voo Dracônico (Nvl 5)"])),
            ("Gnomo", "Mentes astutas e curiosas, dotados de magia inata e astúcia mental.", 8, "Pequeno", json.dumps(["Astúcia Gnomica", "Visão no Escuro (18m)", "Descendência Feérica/Rochedo"])),
            ("Tiefling", "Herdeiros de linhagens infernais ou abissais com chifres e cauda.", 9, "Médio", json.dumps(["Visão no Escuro (18m)", "Legado Infernal", "Resistência ao Fogo"])),
            ("Aasimar", "Abençoados com luz divina e asas celestiais.", 9, "Médio", json.dumps(["Visão no Escuro (18m)", "Mãos Curativas", "Revelação Celestial"]))
        ]
        cursor.executemany("INSERT INTO species (name, description, speed, size, traits_json) VALUES (?, ?, ?, ?, ?)", species_list)

    # Classes 2024 em pt-BR
    cursor.execute("SELECT COUNT(*) FROM classes")
    if cursor.fetchone()[0] == 0:
        classes_list = [
            ("Guerreiro", 10, "FOR ou DES", "FOR, CON", "Mestre em todas as armas e armaduras, focado no combate tático e maestria em armas."),
            ("Mago", 6, "INT", "INT, SAB", "Conjurador escolar experiente que manipula o tecido da realidade através de seu Livro de Magias."),
            ("Clérigo", 8, "SAB", "SAB, CAR", "Guerreiro sagrado investido com os poderes divinos de sua divindade patrona."),
            ("Ladino", 8, "DES", "DES, INT", "Especialista em pericias, ataques furtivos mortais e movimentação ágil."),
            ("Bárbaro", 12, "FOR", "FOR, CON", "Combatente impulsionado pela fúria primal e durabilidade inabalável."),
            ("Bardo", 8, "CAR", "DES, CAR", "Mestre da inspiração, magia de som e versatilidade em pericias."),
            ("Druida", 8, "SAB", "INT, SAB", "Guardião da natureza capaz de conjurar magias elementais e se transformar em feras."),
            ("Monge", 8, "DES, SAB", "FOR, DES", "Mestre das artes marciais e canalização de energia ki/foco corporal."),
            ("Paladino", 10, "FOR, CAR", "SAB, CAR", "Campeão juramentado que une combate pesado com punição divina."),
            ("Patrulheiro", 10, "DES, SAB", "FOR, DES", "Caçador das terras selvagens especializado em rastreamento e combate ágil."),
            ("Feiticeiro", 6, "CAR", "CON, CAR", "Conjurador nato cuja magia flui de sua própria linhagem exótica."),
            ("Bruxo", 8, "CAR", "SAB, CAR", "Pactuante de um patrono extraordinário dotado de rajadas místicas e invocações.")
        ]
        cursor.executemany("INSERT INTO classes (name, hit_die, primary_ability, saving_throws, description) VALUES (?, ?, ?, ?, ?)", classes_list)

    # Antecedentes 2024 em pt-BR
    cursor.execute("SELECT COUNT(*) FROM backgrounds")
    if cursor.fetchone()[0] == 0:
        backgrounds_list = [
            ("Acólito", "Devotado ao serviço de um templo ou fé divina.", "Iniciado em Magia (Clérigo)", "INT, SAB, CAR", "Intuição, Religião"),
            ("Artesão da Guilda", "Mestre em um ofício ou guilda mercantil.", "Artífice / Habilidoso", "FOR, DES, INT", "Persuasão, Investigação"),
            ("Charlatão", "Mestre em disfarces, golpes e manipulação social.", "Iniciado em Magia / Habilidoso", "DES, INT, CAR", "Enganação, Prestidigitação"),
            ("Criminoso", "Histórico de infração às leis nas sombras das cidades.", "Alerta", "DES, CON, INT", "Furtividade, Enganação"),
            ("Eremita", "Anos de isolamento e contemplação de segredos arcanos.", "Alerta / Conhecimento", "CON, INT, SAB", "Medicina, Religião"),
            ("Guarda", "Treinado na patrulha da cidade e manutenção da ordem.", "Vigilante", "FOR, CON, SAB", "Atletismo, Percepção"),
            ("Nobre", "Nascido em uma casa abastada e instruído na diplomacia.", "Inspirador", "DES, INT, CAR", "História, Persuasão"),
            ("Sábio", "Dedicou a vida ao estudo de tomo antigos e mistérios.", "Iniciado em Magia (Mago)", "INT, SAB, CAR", "Arcanismo, História"),
            ("Soldado", "Veterano de batalhas militares e disciplina de combate.", "Combatente Forte", "FOR, DES, CON", "Atletismo, Intimidação"),
            ("Vagabundo", "Cresceu nas ruas aprendendo a sobreviver na astúcia.", "Pés Ligeiros", "DES, CON, SAB", "Prestidigitação, Furtividade")
        ]
        cursor.executemany("INSERT INTO backgrounds (name, description, origin_feat, ability_boosts, skill_proficiencies) VALUES (?, ?, ?, ?, ?)", backgrounds_list)

    # Talentos de Origem 2024 em pt-BR
    cursor.execute("SELECT COUNT(*) FROM origin_feats")
    if cursor.fetchone()[0] == 0:
        feats_list = [
            ("Alerta", "Origem", "Você ganha +5 de Bônus na Iniciativa e pode trocar sua ordem de iniciativa com um aliado voluntário no início do combate."),
            ("Iniciado em Magia", "Origem", "Aprenda 2 Truques e 1 Magia de Nível 1 da lista de Mago, Clérigo ou Druida. Você pode conjurar a magia de Nível 1 gratuitamente 1x por descanso longo."),
            ("Inspirador", "Origem", "Após um descanso curto ou longo, você dá Pontos de Vida Temporários a seus aliados igual ao seu Bônus de Proficiência + Modificador de Carisma."),
            ("Combatente Forte", "Origem", "Ao errar um ataque com uma arma de combate corpo a corpo, você ainda causa dano igual ao seu Modificador de Força."),
            ("Habilidoso", "Origem", "Você ganha proficiência em 3 Perícias ou Ferramentas à sua escolha."),
            ("Curandeiro", "Origem", "Você pode usar um Kit de Curandeiro para estabilizar criaturas e restaurar PV adicionais ao gastar Dados de Vida durante um descanso.")
        ]
        cursor.executemany("INSERT INTO origin_feats (name, category, description) VALUES (?, ?, ?)", feats_list)

    # Magias 2024 em pt-BR
    cursor.execute("SELECT COUNT(*) FROM spells")
    if cursor.fetchone()[0] == 0:
        spells_list = [
            ("Míssil Mágico", 1, "Evocação", "1 Ação", "36 metros", "V, S", "Instantânea", json.dumps(["Mago", "Feiticeiro"]), "Você cria 3 dardos brilhantes de força mágica. Cada dardo atinge uma criatura à sua escolha e causa 1d4 + 1 de dano de Força."),
            ("Curar Ferimentos", 1, "Evocação", "1 Ação", "Toque", "V, S", "Instantânea", json.dumps(["Clérigo", "Bardo", "Druida", "Paladino", "Patrulheiro"]), "Uma criatura que você tocar recupera um número de Pontos de Vida igual a 2d8 + seu modificador de habilidade de conjuração."),
            ("Escudo Mágico (Shield)", 1, "Abjuração", "1 Ação de Reação", "Pessoal", "V, S", "1 rodada", json.dumps(["Mago", "Feiticeiro"]), "Uma barreira invisível surge concedendo +5 de Bônus na CA e imunidade a Míssil Mágico até o início do seu próximo turno."),
            ("Bola de Fogo", 3, "Evocação", "1 Ação", "45 metros", "V, S, M", "Instantânea", json.dumps(["Mago", "Feiticeiro"]), "Uma explosão de chamas de 6m de raio causa 8d6 de dano de Fogo a todas as criaturas na área (Salvaguarda de DES para metade)."),
            ("Truque: Rajada Mística", 0, "Evocação", "1 Ação", "36 metros", "V, S", "Instantânea", json.dumps(["Bruxo"]), "Um feixe de energia roxa dispara em direção a uma criatura causando 1d10 de dano de Força."),
            ("Truque: Prestidigitação", 0, "Transmutação", "1 Ação", "3 metros", "V, S", "Até 1 hora", json.dumps(["Mago", "Bardo", "Feiticeiro", "Bruxo"]), "Cria um pequeno efeito mágico menor, limpa/suja objetos, acende velas ou altera o sabor de alimentos."),
            ("Truque: Chama Sagrada", 0, "Evocação", "1 Ação", "18 metros", "V, S", "Instantânea", json.dumps(["Clérigo"]), "Luz radiante desce sobre uma criatura causando 1d8 de dano Radiante (Salvaguarda de DES nega)."),
            ("Invisibilidade", 2, "Ilusão", "1 Ação", "Toque", "V, S, M", "Concentração (até 1 hora)", json.dumps(["Mago", "Bardo", "Feiticeiro", "Bruxo"]), "Uma criatura tocada torna-se invisível até atacar ou conjurar uma magia."),
            ("Onda Trovante", 1, "Evocação", "1 Ação", "Pessoal (cubo de 4.5m)", "V, S", "Instantânea", json.dumps(["Mago", "Bardo", "Feiticeiro", "Druida"]), "Um estrondo thunderous empurra inimigos 3m para trás e causa 2d8 de dano Trovão."),
            ("Voo", 3, "Transmutação", "1 Ação", "Toque", "V, S, M", "Concentração (até 10 min)", json.dumps(["Mago", "Feiticeiro", "Bruxo"]), "Concede deslocamento de voo de 18 metros a uma criatura voluntária.")
        ]
        cursor.executemany("INSERT INTO spells (name, level, school, casting_time, range_area, components, duration, classes_json, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", spells_list)


    # Equipamentos em pt-BR
    cursor.execute("SELECT COUNT(*) FROM equipment")
    if cursor.fetchone()[0] == 0:
        equip_list = [
            ("Espada Longa", "Arma Marcial", "15 po", 1.5, "1d8", "Cortante", "Versátil (1d10), Maestria: Podar", "Uma lâmina de aço de dois gumes versátil e resistente."),
            ("Adaga", "Arma Simples", "2 po", 0.5, "1d4", "Perfurante", "Acuidade, Leve, Arremesso (6/18m)", "Lâmina curta afiada ideal para ataques rápidos ou ocultação."),
            ("Arco Longo", "Arma Marcial", "50 po", 1.0, "1d8", "Perfurante", "Munição (45/180m), Duas Mãos", "Arco alto de madeira nobre para disparos à distância."),
            ("Cota de Malha", "Armadura Pesada", "75 po", 25.0, "CA 16", "Nenhum", "Requisito FOR 13, Desvantagem em Furtividade", "Armadura composta de anéis metálicos entrelaçados."),
            ("Gibão de Couro", "Armadura Leve", "10 po", 5.0, "CA 11 + DES", "Nenhum", "Nenhum", "Couro trabalhado e reforçado com rebites."),
            ("Escudo", "Escudo", "10 po", 3.0, "+2 CA", "Nenhum", "Ocupa uma mão", "Escudo de madeira reforçado com ferro."),
            ("Kit de Explorador", "Equipamento", "10 po", 10.0, "-", "-", "Mochila, saco de dormir, rações (10 dias), tochas", "Pacote essencial de equipamentos para aventuras no campo."),
            ("Poção de Cura", "Consumível", "50 po", 0.5, "2d4 + 2", "Cura", "Ação bônus para beber (2024)", "Líquido vermelho brilhante que restaura 2d4 + 2 Pontos de Vida.")
        ]
        cursor.executemany("INSERT INTO equipment (name, type, cost, weight, damage, damage_type, properties, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", equip_list)

    conn.commit()

# CRUD de Personagens

def save_character(character: Character) -> int:
    """Salva ou atualiza um personagem no banco de dados SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    data_json = json.dumps(character.to_dict(), ensure_ascii=False)

    if character.id is None:
        cursor.execute(
            "INSERT INTO characters (name, campaign, species, data_json) VALUES (?, ?, ?, ?)",
            (character.name, character.campaign, character.species, data_json)
        )
        character.id = cursor.lastrowid
    else:
        cursor.execute(
            "UPDATE characters SET name = ?, campaign = ?, species = ?, data_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (character.name, character.campaign, character.species, data_json, character.id)
        )
    conn.commit()
    conn.close()
    return character.id

def load_character(char_id: int) -> Optional[Character]:
    """Carrega um personagem pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, data_json FROM characters WHERE id = ?", (char_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = json.loads(row["data_json"])
        data["id"] = row["id"]
        return Character.from_dict(data)
    return None

def list_characters() -> List[Dict[str, Any]]:
    """Lista todos os personagens cadastrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, campaign, species, data_json, updated_at FROM characters ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        data = json.loads(r["data_json"])
        data["id"] = r["id"]
        char_obj = Character.from_dict(data)
        result.append({
            "id": r["id"],
            "name": char_obj.name,
            "campaign": char_obj.campaign,
            "species": char_obj.species,
            "classes_str": " / ".join([f"{c.class_name} {c.level}" for c in char_obj.classes]) if char_obj.classes else "Sem Classe",
            "total_level": char_obj.total_level,
            "avatar_b64": char_obj.avatar_b64,
            "updated_at": r["updated_at"],
            "character_obj": char_obj
        })
    return result

def delete_character(char_id: int):
    """Exclui um personagem pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
    conn.commit()
    conn.close()

def duplicate_character(char_id: int) -> Optional[int]:
    """Duplica um personagem existente."""
    char = load_character(char_id)
    if char:
        char.id = None
        char.name = f"{char.name} (Cópia)"
        return save_character(char)
    return None

# Métodos de consulta de dados do livro de regras
def fetch_all_species() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM species ORDER BY name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def fetch_all_classes() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classes ORDER BY name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def fetch_all_backgrounds() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backgrounds ORDER BY name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def fetch_all_origin_feats() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM origin_feats ORDER BY name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def fetch_all_spells() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spells ORDER BY level ASC, name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def fetch_all_equipment() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment ORDER BY type ASC, name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
