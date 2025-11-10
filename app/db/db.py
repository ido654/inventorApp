import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "bot.db")

# ==========================
# 🔌 ניהול חיבורי מסד נתונים
# ==========================

@contextmanager
def get_connection():
    """חיבור ל-DB במצב כתיבה, כולל ניהול commit/rollback."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"[DB ERROR] Failed to connect or operate on DB file: {DB_PATH}")
        print(f"Error details: {e}")
        # במקרה של שגיאה, אין צורך לנסות commit, אבל חשוב לסגור את החיבור
        if conn:
            conn.close() 
        # כאן אתה יכול לבחור להעלות שגיאה מחדש או פשוט להפסיק
        raise # מעלה את השגיאה הלאה כדי שהתהליך ייכשל אם ה-DB חיוני
    except Exception as e:
        print(f"[GENERAL DB ERROR] An unexpected error occurred: {e}")
        if conn:
            conn.close()
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_readonly_connection():
    """חיבור ל-DB במצב קריאה בלבד (ללא commit וללא נעילות כתיבה)."""
    conn = None
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.OperationalError as e:
        print(f"[DB ERROR] Failed to connect or operate on DB file: {DB_PATH}")
        print(f"Error details: {e}")
        # במקרה של שגיאה, אין צורך לנסות commit, אבל חשוב לסגור את החיבור
        if conn:
            conn.close() 
        # כאן אתה יכול לבחור להעלות שגיאה מחדש או פשוט להפסיק
        raise # מעלה את השגיאה הלאה כדי שהתהליך ייכשל אם ה-DB חיוני
    except Exception as e:
        print(f"[GENERAL DB ERROR] An unexpected error occurred: {e}")
        if conn:
            conn.close()
        raise
    finally:
        if conn:
            conn.close()

# ==========================
# 🧱 יצירת הטבלאות
# ==========================
            
def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY UNIQUE ,
                    owner TEXT ,
                    category TEXT 
                    )
                    """)
        
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS relations (
                    item_id INTEGER,
                    related_id INTEGER,
                    PRIMARY  KEY (item_id , related_id),
                    FOREIGN KEY (item_id) REFERENCES items(id),
                    FOREIGN KEY (related_id) REFERENCES items(id)
            )
        """)

        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    date TEXT DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)

        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                date TEXT DEFAULT (datetime('now', 'localtime')),
                is_return INTEGER DEFAULT 0,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY UNIQUE NOT NULL, 
                display_name TEXT NOT NULL
            )
        """)

        print("✅ Database initialized successfully.")

# ==========================
# 📦 CRUD: USERS
# ==========================
def register_user(user_id, display_name):
    """מוסיף או מחליף שם תצוגה למשתמש קיים."""
    with get_connection() as conn:
        cur = conn.cursor()
        # שימוש ב-INSERT OR REPLACE כדי לאפשר למשתמש לעדכן את שמו
        cur.execute(
            "INSERT OR REPLACE INTO users (user_id, display_name) VALUES (?, ?)",
            (user_id, display_name)
        )

def get_user_display_name(user_id):
    """מחזיר את שם התצוגה של המשתמש הרשום."""
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT display_name FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
        return result[0] if result else None

# ==========================
# 📦 CRUD: ITEMS
# ==========================

def add_item(item_id, owner , category):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO items (id , owner , category) VALUES (?,?,?)" , (item_id , owner , category))
        return cur.lastrowid

def get_item (item_id):
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM items WHERE id = ?" , (item_id,))
        return cur.fetchall()
    
def get_all_items():
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM items")
        return cur.fetchall()
        

def delete_item(item_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM items WHERE id = ?" , (item_id,))

# ==========================
# 🔗 CRUD: RELATIONS
# ==========================
        
def add_relation(item_id , related_id):
    with get_connection() as conn:
        cur= conn.cursor()
        cur.execute("INSERT INTO relations (item_id , related_id) VALUES (?,?)" , (item_id , related_id))

def get_all_relations():
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT r.related_id , i.owner , i.category
                    FROM relations AS r
                    JOIN items AS i ON i.id = r.related_id
                    """)
        return cur.fetchall()

def get_relations(item_id):
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.related_id, i.owner, i.category
            FROM relations AS r
            JOIN items AS i ON i.id = r.related_id
            WHERE r.item_id = ?
        """, (item_id,))
        return cur.fetchall()

def delete_relation(item_id, related_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM relations WHERE item_id = ? AND related_id = ?",
            (item_id, related_id)
        )

# ==========================
# 📋 CRUD: RECORDS
# ==========================
def get_record(item_id):
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM records WHERE item_id = ?" , (item_id,))
        return cur.fetchall()
    
def add_record(new_name, item_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM items WHERE id = ? LIMIT 1" , (item_id, ))
        if not cur.fetchone ():
            return "ITEM_NOT_FOUND"
        cur.execute("SELECT name FROM records WHERE item_id = ?" , (item_id,))
        existing_record = cur.fetchone()
        if existing_record:
            old_name = existing_record[0]
            cur.execute("INSERT INTO history (name , item_id, is_return) VALUES (?,?,1)" , (old_name , item_id))
            cur.execute("DELETE FROM records WHERE item_id = ? " , (item_id,))
            takeover_happened = True
        else:
            takeover_happened = False
        cur.execute("INSERT INTO records (name, item_id) VALUES (?,?)" , (new_name , item_id))
        cur.execute("INSERT INTO history (name, item_id, is_return) VALUES (?, ?, 0)" , (new_name , item_id)) 
        return "TAKEOVER" if takeover_happened else "SUCCESS"
       

def remove_record(name,  item_id ):
    """כאשר מחזירים ציוד"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM records WHERE item_id = ?" , (item_id,))
        existing_record = cur.fetchone()
        if not existing_record:
            return "NOT_TAKEN"
        
        
        cur.execute("DELETE FROM records WHERE item_id = ?", (item_id,))
        cur.execute(
            "INSERT INTO history (name, item_id, is_return) VALUES (?, ?, 1)",
            (name, item_id)
        )
        return 'SUCCESS'
    

def remove_history(item_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM history WHERE item_id = ?", (item_id,))

def get_active_records():
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT item_id , name , date
            FROM records AS r
            ORDER BY r.date DESC
        """)
        return cur.fetchall()
    
# ==========================
# 🕒 CRUD: HISTORY
# ==========================
    
def get_history():
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM history
            ORDER BY date DESC
        """)
        return cur.fetchall()

def get_history_by_time(days):
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT h.item_id, h.name, h.is_return, date(h.date)
                    FROM history AS h
                    JOIN (
                        SELECT item_id, MAX(date) AS max_date
                        FROM history
                        WHERE date >= datetime('now', 'localtime', ?)
                        GROUP BY item_id
                    ) AS latest
                    ON h.item_id = latest.item_id AND h.date = latest.max_date
                    ORDER BY h.date DESC;

                    """ , (f'-{days} days' ,) )
        return cur.fetchall()

# ==========================
# 🕒 CALCULTE: CALCULATE
# ==========================
    
def get_total_count():
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT category , COUNT(id) FROM items GROUP BY category")
        return cur.fetchall()

def get_inventory_summary():
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    -- יצירת טבלה שמשלבת את הפריטים והפריטים הנלווים אליהם שרשומים בטבלת הרקורד
                    WITH taken_items AS (
                        SELECT rec.item_id  , i.category
                        FROM records AS rec
                        JOIN items AS i ON i.id = rec.item_id

                        UNION

                        SELECT rel.item_id , i.category 
                        FROM relations AS rel
                        JOIN items AS i ON i.id = rel.item_id
                        JOIN records AS rec ON rec.item_id = rel.related_id
                    )
                    SELECT i.category, COUNT(i.id) AS total_count , (COUNT(i.id) - COUNT(t.item_id)) AS rest_count
                    FROM items AS i
                    LEFT JOIN taken_items AS t ON t.item_id = i.id
                    GROUP BY i.category
                    """)        
        return cur.fetchall() 

def get_taken_items_with_relations():
    with get_readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT rec.item_id AS main_item_id  , i.category
                    FROM records AS rec
                    JOIN items AS i ON i.id = rec.item_id

                    UNION

                    SELECT rel.item_id , i.category 
                    FROM relations AS rel
                    JOIN items AS i ON i.id = rel.item_id
                    JOIN records AS rec ON rec.item_id = rel.related_id
                    """)
        return cur.fetchall()



