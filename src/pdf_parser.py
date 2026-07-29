import os
import re
import sqlite3
import json
from typing import Dict, List, Any, Optional

try:
    import pypdf
except ImportError:
    try:
        import PyPDF2 as pypdf
    except ImportError:
        pypdf = None

from src.database import get_connection

DOCS_DIR = "./docs"

def ensure_docs_folder():
    """Garante que a pasta ./docs/ existe no ambiente."""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)

def scan_and_parse_pdf_docs() -> Dict[str, int]:
    """
    Varre a pasta ./docs/ por arquivos PDF (como phb2024.pdf), extrai textos e cataloga dados em pt-BR no SQLite.
    Retorna o número de itens processados por categoria.
    """
    ensure_docs_folder()

    if not pypdf:
        return {"status": 0, "msg": "Biblioteca pypdf/PyPDF2 não disponível."}

    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        return {"status": 0, "msg": "Nenhum arquivo PDF encontrado em ./docs/"}

    stats = {"spells": 0, "classes": 0, "species": 0, "backgrounds": 0, "files_scanned": len(pdf_files)}

    for pdf_file in pdf_files:
        pdf_path = os.path.join(DOCS_DIR, pdf_file)
        try:
            reader = pypdf.PdfReader(pdf_path)
            full_text = ""
            # Extrai até as primeiras 100 páginas para evitar estolamento em PDFs gigantes
            max_pages = min(len(reader.pages), 100)
            for i in range(max_pages):
                text = reader.pages[i].extract_text()
                if text:
                    full_text += text + "\n"

            # Parse simples de seções de magias e dados
            spells_found = parse_and_insert_spells_from_text(full_text)
            stats["spells"] += spells_found

        except Exception as e:
            print(f"Erro ao processar PDF {pdf_file}: {e}")

    return stats

def parse_and_insert_spells_from_text(text: str) -> int:
    """Procura por magias no texto extraído do PDF e insere no banco de dados se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # Expressão regular básica para capturar blocos de magia (Nome, Nível, Escola)
    # Ex: Bola de Fogo / Fireball - Nível 3 Evocação
    spell_pattern = re.compile(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç\s]{3,30})\n(?:Magia|Truque|Level|Nível)\s*(\d)?\s*([A-Za-zÁ-ú]+)?', re.IGNORECASE)

    matches = spell_pattern.findall(text)
    count = 0
    for match in matches:
        name_candidate = match[0].strip()
        level_val = int(match[1]) if match[1] and match[1].isdigit() else 1
        school_val = match[2].strip() if match[2] else "Evocação"

        if len(name_candidate) > 3 and not any(kw in name_candidate.lower() for kw in ["capítulo", "página", "regras", "índice"]):
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO spells (name, level, school, casting_time, range_area, components, duration, classes_json, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name_candidate, level_val, school_val, "1 Ação", "18 metros", "V, S", "Instantânea", json.dumps(["Mago", "Clérigo"]), f"Magia extraída automaticamente de arquivo PDF de referência ({name_candidate})."))
                if cursor.rowcount > 0:
                    count += 1
            except Exception:
                pass

    conn.commit()
    conn.close()
    return count
