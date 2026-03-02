import sqlite3
from utils import paths

#--- Card table
# Name
# ID
# phrase
# translation
# context
# frame path
# audio path

#---Lang Config
#Name
#ID
#From_Language
#To_Language

def get_db_connection():
    conn = sqlite3.connect(paths.DATA_BASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create Card table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phrase TEXT,
                translation TEXT,
                context TEXT,
                frame_path TEXT,
                audio_path TEXT
            )
        ''')
        
        # Create LangConfig table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lang_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                from_language TEXT,
                to_language TEXT
            )
        ''')
        conn.commit()




# Initialize on load
init_db()