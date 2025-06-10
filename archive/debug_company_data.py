"""
Debug script to check company additional data sources configuration
"""
import sqlite3
import json

def check_company_data():
    """Check what companies have additional data sources configured"""
    try:
        conn = sqlite3.connect("user_management.db")
        cursor = conn.cursor()
        
        # Check companies table structure
        cursor.execute("PRAGMA table_info(companies)")
        columns = cursor.fetchall()
        print("Companies table columns:")
        for col in columns:
            print(f"  {col}")
        
        print("\n" + "="*50 + "\n")
        
        # Get all companies
        cursor.execute("SELECT id, company_name, user_preferences FROM companies")
        companies = cursor.fetchall()
        
        print("Company Additional Data Sources:")
        for company in companies:
            company_id, name, prefs_json = company
            print(f"\nCompany ID: {company_id}")
            print(f"Company Name: {name}")
            
            if prefs_json:
                try:
                    prefs = json.loads(prefs_json)
                    additional_data = prefs.get('additional_data', [])
                    print(f"Additional Data Sources: {additional_data}")
                except json.JSONDecodeError:
                    print("Invalid JSON in user_preferences")
            else:
                print("No preferences found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_company_data()