import sqlite3
import json
import os

DB_PATH = "data/database.db"

def init_db():
    """Cria o banco de dados e as tabelas se não existirem."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de Jogadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Tabela de Esportes (attributes será uma string separada por vírgulas, ex: "Passe,Chute,Fisico")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            attributes TEXT NOT NULL
        )
    ''')

    # Tabela de Avaliações (scores será um JSON, ex: {"Passe": 8, "Chute": 7, "Fisico": 6})
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            player_id INTEGER,
            sport_id INTEGER,
            scores TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id),
            FOREIGN KEY (sport_id) REFERENCES sports (id)
        )
    ''')

    conn.commit()
    conn.close()

# --- FUNÇÕES PARA JOGADORES ---

def add_player(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Jogador já existe
    finally:
        conn.close()

def get_players():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM players")
    players = cursor.fetchall()
    conn.close()
    return players

def delete_player(player_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    # Opcional: deletar avaliações associadas a este jogador
    cursor.execute("DELETE FROM evaluations WHERE player_id = ?", (player_id,))
    conn.commit()
    conn.close()

# --- FUNÇÕES PARA ESPORTES ---

def add_sport(name, attributes_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    attributes_str = ",".join(attributes_list)
    try:
        cursor.execute("INSERT INTO sports (name, attributes) VALUES (?, ?)", (name, attributes_str))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_sports():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, attributes FROM sports")
    sports = cursor.fetchall()
    conn.close()
    return sports

def delete_sport(sport_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sports WHERE id = ?", (sport_id,))
    cursor.execute("DELETE FROM evaluations WHERE sport_id = ?", (sport_id,))
    conn.commit()
    conn.close()

# --- FUNÇÕES PARA AVALIAÇÕES ---

def add_evaluation(date, player_id, sport_id, scores_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    scores_json = json.dumps(scores_dict)
    cursor.execute(
        "INSERT INTO evaluations (date, player_id, sport_id, scores) VALUES (?, ?, ?, ?)",
        (date, player_id, sport_id, scores_json)
    )
    conn.commit()
    conn.close()

def get_evaluations(sport_id=None, player_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT e.id, e.date, p.name, s.name, e.scores, e.player_id, e.sport_id
        FROM evaluations e
        JOIN players p ON e.player_id = p.id
        JOIN sports s ON e.sport_id = s.id
        WHERE 1=1
    """
    params = []
    
    if sport_id:
        query += " AND e.sport_id = ?"
        params.append(sport_id)
    if player_id:
        query += " AND e.player_id = ?"
        params.append(player_id)
        
    query += " ORDER BY e.date DESC"
    
    cursor.execute(query, params)
    evaluations = cursor.fetchall()
    conn.close()
    return evaluations

def update_evaluation(evaluation_id, scores_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    scores_json = json.dumps(scores_dict)
    cursor.execute("UPDATE evaluations SET scores = ? WHERE id = ?", (scores_json, evaluation_id))
    conn.commit()
    conn.close()

def delete_evaluation(evaluation_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluations WHERE id = ?", (evaluation_id,))
    conn.commit()
    conn.close()