"""
Field Mapping Manager for DSA Template Flexibility
Handles custom CSV format mapping and DSA-specific configurations
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime

class FieldMappingManager:
    """Manages field mappings for different DSA partners"""
    
    def __init__(self, db_path: str = "field_mappings.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database for field mappings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS field_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dsa_id TEXT NOT NULL,
                dsa_name TEXT NOT NULL,
                mapping_config TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mapping_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dsa_id TEXT NOT NULL,
                old_mapping TEXT,
                new_mapping TEXT,
                changed_by TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_mapping(self, dsa_id: str, dsa_name: str, mapping: Dict[str, str]) -> bool:
        """Save field mapping configuration for a DSA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if mapping exists
            cursor.execute("SELECT mapping_config FROM field_mappings WHERE dsa_id = ?", (dsa_id,))
            existing = cursor.fetchone()
            
            mapping_json = json.dumps(mapping)
            
            if existing:
                # Update existing mapping
                cursor.execute("""
                    UPDATE field_mappings 
                    SET mapping_config = ?, dsa_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE dsa_id = ?
                """, (mapping_json, dsa_name, dsa_id))
                
                # Save to history
                cursor.execute("""
                    INSERT INTO mapping_history (dsa_id, old_mapping, new_mapping, changed_by)
                    VALUES (?, ?, ?, ?)
                """, (dsa_id, existing[0], mapping_json, "system"))
            else:
                # Insert new mapping
                cursor.execute("""
                    INSERT INTO field_mappings (dsa_id, dsa_name, mapping_config)
                    VALUES (?, ?, ?)
                """, (dsa_id, dsa_name, mapping_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving mapping: {str(e)}")
            return False
    
    def get_mapping(self, dsa_id: str) -> Optional[Dict[str, Any]]:
        """Get field mapping for a specific DSA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT dsa_name, mapping_config, created_at, updated_at FROM field_mappings 
                WHERE dsa_id = ? AND is_active = 1
            """, (dsa_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                mapping_config = json.loads(result[1]) if result[1] else {}
                return {
                    'dsa_name': result[0],
                    'mapping': mapping_config,
                    'created_at': result[2],
                    'updated_at': result[3]
                }
            return None
        except Exception as e:
            st.error(f"Error getting mapping: {str(e)}")
            return None
    
    def get_all_mappings(self) -> List[Dict[str, Any]]:
        """Get all active field mappings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT dsa_id, dsa_name, mapping_config, created_at, updated_at
                FROM field_mappings 
                WHERE is_active = 1
                ORDER BY dsa_name
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            mappings = []
            for row in results:
                mappings.append({
                    "dsa_id": row[0],
                    "dsa_name": row[1],
                    "mapping": json.loads(row[2]),
                    "created_at": row[3],
                    "updated_at": row[4]
                })
            
            return mappings
        except Exception as e:
            st.error(f"Error getting all mappings: {str(e)}")
            return []
    
    def delete_mapping(self, dsa_id: str) -> bool:
        """Soft delete a field mapping"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE field_mappings 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE dsa_id = ?
            """, (dsa_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error deleting mapping: {str(e)}")
            return False

def render_field_mapping_management():
    """Render field mapping management interface"""
    st.header("🔗 DSA Field Mapping Management")
    st.write("Configure custom CSV field mappings for different DSA partners")
    
    mapping_manager = FieldMappingManager()
    
    # Tabs for different functions
    tab1, tab2, tab3 = st.tabs(["Create/Edit Mapping", "View Mappings", "Test Mapping"])
    
    with tab1:
        st.subheader("Create or Edit Field Mapping")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dsa_id = st.text_input("DSA ID", placeholder="e.g., DSA_001")
            dsa_name = st.text_input("DSA Name", placeholder="e.g., ABC Financial Services")
        
        with col2:
            st.info("Standard Fields Available:")
            st.write("• credit_score, foir, dpd30plus")
            st.write("• enquiry_count, monthly_income")
            st.write("• account_vintage, avg_monthly_balance")
            st.write("• employment_tenure, company_stability")
            st.write("• And 14 more variables...")
        
        st.subheader("Field Mapping Configuration")
        st.write("Map DSA CSV columns to standard scoring variables:")
        
        # Standard variables for mapping
        standard_vars = [
            "credit_score", "foir", "dpd30plus", "enquiry_count", "monthly_income",
            "credit_vintage", "loan_mix_type", "loan_completion_ratio", "defaulted_loans",
            "job_type", "employment_tenure", "company_stability", "account_vintage",
            "avg_monthly_balance", "bounce_frequency", "geographic_risk",
            "mobile_number_vintage", "digital_engagement", "unsecured_loan_amount",
            "outstanding_amount_percent", "our_lender_exposure", "channel_type"
        ]
        
        # Load existing mapping if available
        existing_mapping = {}
        if dsa_id:
            existing_mapping = mapping_manager.get_mapping(dsa_id) or {}
        
        # Create mapping inputs
        mapping = {}
        st.write("**Format: DSA Column Name → Standard Variable**")
        
        # Use columns for better layout
        col1, col2 = st.columns(2)
        
        for i, var in enumerate(standard_vars):
            if i % 2 == 0:
                with col1:
                    dsa_column = st.text_input(
                        f"DSA field for {var}",
                        value=existing_mapping.get(var, ""),
                        key=f"mapping_{var}",
                        placeholder=f"e.g., cibil_score"
                    )
            else:
                with col2:
                    dsa_column = st.text_input(
                        f"DSA field for {var}",
                        value=existing_mapping.get(var, ""),
                        key=f"mapping_{var}",
                        placeholder=f"e.g., monthly_sal"
                    )
            
            if dsa_column.strip():
                mapping[dsa_column.strip()] = var
        
        # Save mapping
        if st.button("Save Field Mapping", type="primary"):
            if dsa_id and dsa_name and mapping:
                if mapping_manager.save_mapping(dsa_id, dsa_name, mapping):
                    st.success(f"Field mapping saved for {dsa_name}")
                    st.rerun()
            else:
                st.error("Please provide DSA ID, name, and at least one field mapping")
    
    with tab2:
        st.subheader("Existing Field Mappings")
        
        mappings = mapping_manager.get_all_mappings()
        
        if mappings:
            for idx, mapping_data in enumerate(mappings):
                with st.expander(f"{mapping_data['dsa_name']} ({mapping_data['dsa_id']})"):
                    st.write(f"**Created:** {mapping_data['created_at']}")
                    st.write(f"**Last Updated:** {mapping_data['updated_at']}")
                    
                    st.write("**Field Mappings:**")
                    for dsa_field, std_field in mapping_data['mapping'].items():
                        st.write(f"• `{dsa_field}` → `{std_field}`")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit {mapping_data['dsa_id']}", key=f"edit_{mapping_data['dsa_id']}_{idx}"):
                            st.session_state[f"edit_dsa_id"] = mapping_data['dsa_id']
                            st.rerun()
                    
                    with col2:
                        if st.button(f"Delete {mapping_data['dsa_id']}", key=f"delete_{mapping_data['dsa_id']}_{idx}", type="secondary"):
                            if mapping_manager.delete_mapping(mapping_data['dsa_id']):
                                st.success(f"Mapping deleted for {mapping_data['dsa_name']}")
                                st.rerun()
        else:
            st.info("No field mappings configured yet.")
    
    with tab3:
        st.subheader("Test Field Mapping")
        
        # Select DSA for testing
        mappings = mapping_manager.get_all_mappings()
        if mappings:
            dsa_options = {f"{m['dsa_name']} ({m['dsa_id']})": m['dsa_id'] for m in mappings}
            selected_dsa = st.selectbox("Select DSA to test", options=list(dsa_options.keys()))
            
            if selected_dsa:
                dsa_id = dsa_options[selected_dsa]
                mapping = mapping_manager.get_mapping(dsa_id)
                
                st.write("**Current Mapping:**")
                for dsa_field, std_field in mapping.items():
                    st.write(f"• `{dsa_field}` → `{std_field}`")
                
                # Upload test file
                uploaded_file = st.file_uploader("Upload test CSV file", type=['csv'])
                
                if uploaded_file:
                    try:
                        # Read CSV
                        df = pd.read_csv(uploaded_file)
                        
                        st.write("**Original CSV columns:**")
                        st.write(list(df.columns))
                        
                        # Apply mapping
                        df_mapped = df.rename(columns=mapping)
                        
                        st.write("**After applying mapping:**")
                        st.write(list(df_mapped.columns))
                        
                        # Show preview
                        st.write("**Data Preview (first 5 rows):**")
                        st.dataframe(df_mapped.head())
                        
                        # Show mapping effectiveness
                        mapped_count = len([col for col in df_mapped.columns if col in standard_vars])
                        st.metric("Mapped Standard Variables", f"{mapped_count}/{len(standard_vars)}")
                        
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
        else:
            st.info("No mappings available for testing. Create a mapping first.")

def get_dsa_mapping_options() -> Dict[str, str]:
    """Get available DSA mapping options for dropdowns"""
    mapping_manager = FieldMappingManager()
    mappings = mapping_manager.get_all_mappings()
    return {f"{m['dsa_name']} ({m['dsa_id']})": m['dsa_id'] for m in mappings}