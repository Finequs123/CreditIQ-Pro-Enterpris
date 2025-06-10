import sqlite3
import json

# Create sample field mapping for Finolet
mapping_data = {
    "credit_score": "credit_score",
    "foir": "foir", 
    "enquiry_count": "enquiry_count",
    "monthly_income": "monthly_income",
    "job_type": "job_type",
    "company_stability": "company_stability", 
    "account_vintage": "account_vintage",
    "avg_monthly_balance": "avg_monthly_balance",
    "dpd30plus": "defaulted_loans",
    "bounce_frequency": "outstanding_amount_percent"
}

conn = sqlite3.connect('field_mappings.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS field_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dsa_id TEXT UNIQUE NOT NULL,
        dsa_name TEXT NOT NULL,
        mapping_config TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert/update mapping
cursor.execute("""
    INSERT OR REPLACE INTO field_mappings (dsa_id, dsa_name, mapping_config)
    VALUES (?, ?, ?)
""", ("DSA_002", "Finolet", json.dumps(mapping_data)))

conn.commit()
conn.close()
print("Sample mapping created successfully")