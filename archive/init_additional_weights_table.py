"""
Initialize additional weights configuration table
"""
import sqlite3

def init_additional_weights_table():
    """Create the additional_weights_config table"""
    conn = sqlite3.connect("user_management.db")
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS additional_weights_config (
            company_id INTEGER PRIMARY KEY,
            weights_config TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("Additional weights configuration table created successfully!")

if __name__ == "__main__":
    init_additional_weights_table()