"""
Direct Weights Manager - Bypasses broken configuration system
Directly manages weights in database and updates all components
"""
import sqlite3
import json
import streamlit as st
from typing import Dict, Any

class DirectWeightsManager:
    """Direct database-driven weights management"""
    
    def __init__(self):
        self.db_path = "weights_override.db"
        self.init_database()
    
    def init_database(self):
        """Initialize weights database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_weights (
                variable_name TEXT PRIMARY KEY,
                weight_value REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weights_json TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'AI'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def apply_weights_directly(self, weights: Dict[str, float]) -> bool:
        """Apply weights directly to database and all systems"""
        try:
            # Save to database
            self._save_to_database(weights)
            
            # Save to JSON (for other systems)
            self._save_to_json(weights)
            
            # Update session state weights
            self._update_session_weights(weights)
            
            # Record in history
            self._record_history(weights)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to apply weights: {str(e)}")
            return False
    
    def _save_to_database(self, weights: Dict[str, float]):
        """Save weights to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing weights
        cursor.execute("DELETE FROM active_weights")
        
        # Insert new weights
        for variable, weight in weights.items():
            cursor.execute(
                "INSERT INTO active_weights (variable_name, weight_value) VALUES (?, ?)",
                (variable, weight)
            )
        
        conn.commit()
        conn.close()
    
    def _save_to_json(self, weights: Dict[str, float]):
        """Save weights to JSON file"""
        with open("scoring_weights.json", "w") as f:
            json.dump(weights, f, indent=2)
    
    def _update_session_weights(self, weights: Dict[str, float]):
        """Update session state with new weights"""
        # Clear existing session state
        keys_to_clear = ['config_manager', 'scoring_engine', 'active_weights']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Set new weights in session
        st.session_state.active_weights = weights
        st.session_state.weights_source = 'AI_APPLIED'
    
    def _record_history(self, weights: Dict[str, float]):
        """Record weights application in history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        weights_json = json.dumps(weights)
        cursor.execute(
            "INSERT INTO weight_history (weights_json, source) VALUES (?, ?)",
            (weights_json, "AI_SUGGESTED")
        )
        
        conn.commit()
        conn.close()
    
    def get_active_weights(self) -> Dict[str, float]:
        """Get currently active weights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT variable_name, weight_value FROM active_weights")
        rows = cursor.fetchall()
        conn.close()
        
        return {row[0]: row[1] for row in rows}
    
    def get_weight_history(self) -> list:
        """Get weight application history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT weights_json, applied_at, source 
            FROM weight_history 
            ORDER BY applied_at DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            weights = json.loads(row[0])
            history.append({
                'weights': weights,
                'applied_at': row[1],
                'source': row[2]
            })
        
        return history

def render_direct_weights_button(ai_weights: Dict[str, float]):
    """Render the direct weights application button"""
    if st.button("🔧 Apply AI Weights (Direct)", type="primary", key="direct_apply"):
        manager = DirectWeightsManager()
        
        if manager.apply_weights_directly(ai_weights):
            st.success("✅ AI weights applied directly to system!")
            st.info("🔄 Refresh the page and check Scoring Weights Configuration")
            
            # Show applied weights
            st.subheader("Applied Weights:")
            cols = st.columns(3)
            for i, (var, weight) in enumerate(ai_weights.items()):
                with cols[i % 3]:
                    st.metric(var.replace('_', ' ').title(), f"{weight:.1%}")
        else:
            st.error("❌ Failed to apply weights")

def get_override_weights() -> Dict[str, float]:
    """Get weights from override database if they exist"""
    try:
        manager = DirectWeightsManager()
        weights = manager.get_active_weights()
        if weights:
            return weights
    except:
        pass
    return {}