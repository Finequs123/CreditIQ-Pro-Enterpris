import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """Database manager for storing historical scoring data"""
    
    def __init__(self, db_path: str = "loan_scoring.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Individual applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS individual_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                pan TEXT NOT NULL,
                applicant_data TEXT NOT NULL,
                scoring_result TEXT NOT NULL,
                final_score REAL NOT NULL,
                final_bucket TEXT NOT NULL,
                decision TEXT NOT NULL
            )
        ''')
        
        # Bulk sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bulk_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                total_records INTEGER NOT NULL,
                successful_records INTEGER NOT NULL,
                avg_score REAL,
                session_data TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_individual_result(self, applicant_data: Dict[str, Any], result: Dict[str, Any]):
        """Save individual application result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO individual_applications 
            (timestamp, pan, applicant_data, scoring_result, final_score, final_bucket, decision)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            applicant_data.get('pan', ''),
            json.dumps(applicant_data),
            json.dumps(result),
            result.get('final_score', 0),
            result.get('final_bucket', 'D'),
            result.get('decision', 'Decline')
        ))
        
        conn.commit()
        conn.close()
    
    def save_bulk_results(self, results: List[Dict[str, Any]], session_id: str = None):
        """Save bulk processing results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id is None:
            session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        successful_results = [r for r in results if r['status'] == 'success']
        total_records = len(results)
        successful_records = len(successful_results)
        
        # Calculate average score for successful applications
        avg_score = None
        if successful_records > 0:
            scores = [r['result']['final_score'] for r in successful_results]
            avg_score = sum(scores) / len(scores)
        
        # Save bulk session
        cursor.execute('''
            INSERT INTO bulk_sessions 
            (session_id, timestamp, total_records, successful_records, avg_score, session_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            timestamp,
            total_records,
            successful_records,
            avg_score,
            json.dumps(results)
        ))
        
        # Save individual results from bulk
        for result in successful_results:
            applicant_data = result['applicant_data']
            scoring_result = result['result']
            
            cursor.execute('''
                INSERT INTO individual_applications 
                (timestamp, pan, applicant_data, scoring_result, final_score, final_bucket, decision)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                applicant_data.get('pan', ''),
                json.dumps(applicant_data),
                json.dumps(scoring_result),
                scoring_result.get('final_score', 0),
                scoring_result.get('final_bucket', 'D'),
                scoring_result.get('decision', 'Decline')
            ))
        
        conn.commit()
        conn.close()
    
    def get_individual_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get individual application history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, pan, final_score, final_bucket, decision
            FROM individual_applications 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'pan': row[1],
                'final_score': row[2],
                'final_bucket': row[3],
                'decision': row[4]
            }
            for row in rows
        ]
    
    def get_bulk_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get bulk session history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, timestamp, total_records, successful_records, avg_score
            FROM bulk_sessions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'session_id': row[0],
                'timestamp': row[1],
                'total_records': row[2],
                'successful_records': row[3],
                'avg_score': row[4] if row[4] is not None else 0
            }
            for row in rows
        ]
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results for a specific bulk session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_data FROM bulk_sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
