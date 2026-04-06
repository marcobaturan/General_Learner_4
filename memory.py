import sqlite3
import json

class Memory:
    def __init__(self, db_path="general_learner.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        
        # Guardamos la historia de todo lo que el robot ha hecho/percibido
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chrono_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception TEXT NOT NULL,
                action INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Las reglas generadas durante el sueño: state -> action (con peso heurístico)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception_pattern TEXT NOT NULL,
                target_action INTEGER NOT NULL,
                weight INTEGER DEFAULT 1,
                is_composite INTEGER DEFAULT 0
            )
        """)
        # Migration: Add is_composite if column is missing from previous version
        try:
            cur.execute("ALTER TABLE rules ADD COLUMN is_composite INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass # Column already exists
        
        self.conn.commit()

    def add_chrono(self, perception, action, reward):
        cur = self.conn.cursor()
        perc_str = json.dumps(perception)
        cur.execute("""
            INSERT INTO chrono_memory (perception, action, reward) 
            VALUES (?, ?, ?)
        """, (perc_str, action, reward))
        self.conn.commit()

    def add_rule(self, perception_pattern, action, weight=1, is_composite=0):
        cur = self.conn.cursor()
        perc_str = json.dumps(perception_pattern)
        
        cur.execute("SELECT id, weight FROM rules WHERE perception_pattern = ? AND target_action = ?", (perc_str, action))
        row = cur.fetchone()
        
        if row:
            cur.execute("UPDATE rules SET weight = weight + ? WHERE id = ?", (weight, row['id']))
        else:
            cur.execute("INSERT INTO rules (perception_pattern, target_action, weight, is_composite) VALUES (?, ?, ?, ?)", 
                        (perc_str, action, weight, is_composite))
        self.conn.commit()

    def get_all_chrono(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM chrono_memory ORDER BY id ASC")
        return [dict(row) for row in cur.fetchall()]

    def get_rules(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM rules ORDER BY weight DESC")
        return [dict(row) for row in cur.fetchall()]

    def clear(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM chrono_memory")
        cur.execute("DELETE FROM rules")
        self.conn.commit()
