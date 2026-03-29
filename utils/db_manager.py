import libsql
import json
import streamlit as st

try:
    TURSO_DB_URL = st.secrets["TURSO_DATABASE_URL"]
    TURSO_AUTH_TOKEN = st.secrets["TURSO_AUTH_TOKEN"]
except KeyError:
    st.error("Credenciais do Turso nao encontradas. Configure o st.secrets!")
    st.stop()

def get_connection():
    conn = libsql.connect(database=TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Tenta adicionar a coluna de foto caso ela ainda nao exista no seu banco
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN photo TEXT")
        conn.commit()
    except Exception:
        pass # A coluna ja existe

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            attributes TEXT NOT NULL
        )
    ''')

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

# --- FUNCOES PARA JOGADORES ---
def add_player(name, photo=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO players (name, photo) VALUES (?, ?)", (name, photo))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_player(player_id, new_name, photo=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE players SET name = ?, photo = ? WHERE id = ?", (new_name, photo, player_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_players():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, photo FROM players")
    players = cursor.fetchall()
    conn.close()
    return players

def delete_player(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    cursor.execute("DELETE FROM evaluations WHERE player_id = ?", (player_id,))
    conn.commit()
    conn.close()

# --- FUNCOES PARA ESPORTES ---
def add_sport(name, attributes_dict):
    conn = get_connection()
    cursor = conn.cursor()
    attributes_str = json.dumps(attributes_dict)
    try:
        cursor.execute("INSERT INTO sports (name, attributes) VALUES (?, ?)", (name, attributes_str))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_sport(sport_id, name, attributes_dict):
    conn = get_connection()
    cursor = conn.cursor()
    attributes_str = json.dumps(attributes_dict)
    try:
        cursor.execute("UPDATE sports SET name = ?, attributes = ? WHERE id = ?", (name, attributes_str, sport_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_sports():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, attributes FROM sports")
    sports = cursor.fetchall()
    conn.close()
    return sports

def delete_sport(sport_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sports WHERE id = ?", (sport_id,))
    cursor.execute("DELETE FROM evaluations WHERE sport_id = ?", (sport_id,))
    conn.commit()
    conn.close()

# --- FUNCOES PARA AVALIACOES ---
def add_evaluation(date, player_id, sport_id, scores_dict):
    conn = get_connection()
    cursor = conn.cursor()
    scores_json = json.dumps(scores_dict)
    cursor.execute(
        "INSERT INTO evaluations (date, player_id, sport_id, scores) VALUES (?, ?, ?, ?)",
        (date, player_id, sport_id, scores_json)
    )
    conn.commit()
    conn.close()

def get_evaluations(sport_id=None, player_id=None):
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()
    scores_json = json.dumps(scores_dict)
    cursor.execute("UPDATE evaluations SET scores = ? WHERE id = ?", (scores_json, evaluation_id))
    conn.commit()
    conn.close()

def delete_evaluation(evaluation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluations WHERE id = ?", (evaluation_id,))
    conn.commit()
    conn.close()