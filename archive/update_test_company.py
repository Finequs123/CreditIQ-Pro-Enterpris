"""
Update test company with additional data sources for testing
"""
import sqlite3
import json

def update_test_company():
    """Add additional data sources to test company"""
    conn = sqlite3.connect("user_management.db")
    cursor = conn.cursor()
    
    # Check if companies table exists and has data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
    if not cursor.fetchone():
        print("Companies table does not exist")
        conn.close()
        return
    
    # Check existing companies table structure
    cursor.execute("PRAGMA table_info(companies)")
    columns = cursor.fetchall()
    print("Companies table structure:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check existing companies
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    
    if not companies:
        print("No companies found")
        conn.close()
        return
    
    print("\nExisting companies:")
    for company in companies:
        print(f"Company data: {company}")
    
    # Add additional_data_sources column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE companies ADD COLUMN additional_data_sources TEXT")
        print("\nAdded additional_data_sources column to companies table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("\nadditional_data_sources column already exists")
        else:
            print(f"\nError adding column: {e}")
    
    # Update first company with additional data sources
    test_sources = ["GST Data", "ITR Data", "Utility Bills"]
    
    cursor.execute("""
        UPDATE companies 
        SET additional_data_sources = ? 
        WHERE id = 1
    """, (json.dumps(test_sources),))
    
    conn.commit()
    
    # Verify update
    cursor.execute("SELECT id, company_name, additional_data_sources FROM companies WHERE id = 1")
    result = cursor.fetchone()
    
    if result:
        print(f"\nUpdated company ID {result[0]} ({result[1]}) with additional data sources: {result[2]}")
    
    conn.close()
    print("Test company updated successfully!")

if __name__ == "__main__":
    update_test_company()