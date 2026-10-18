import duckdb
import json
import uuid
from datetime import datetime
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cvd_history.duckdb"))

def get_connection():
    conn = duckdb.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP,
            scan_type VARCHAR,
            target_name VARCHAR,
            functions_scanned INTEGER,
            vulnerabilities_found INTEGER,
            highest_risk_score DOUBLE,
            report_data TEXT
        )
    """)
    return conn

def record_scan(scan_type: str, target_name: str, response_data: dict) -> str:
    scan_id = str(uuid.uuid4())[:8]
    created_at = datetime.utcnow()
    
    functions = response_data.get("functions", [])
    threshold = response_data.get("model_info", {}).get("threshold", 0.5)
    
    functions_scanned = len(functions)
    vuln_count = sum(1 for f in functions if f.get("probability", 0.0) >= threshold)
    highest_risk = float(response_data.get("overall_confidence", 0.0))
    report_json = json.dumps(response_data)
    
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO scan_history (
                id, created_at, scan_type, target_name, 
                functions_scanned, vulnerabilities_found, 
                highest_risk_score, report_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id, created_at, scan_type, target_name,
            functions_scanned, vuln_count, highest_risk, report_json
        ))
    finally:
        conn.close()
        
    return scan_id

def list_scans():
    conn = get_connection()
    try:
        result = conn.execute("""
            SELECT id, created_at, scan_type, target_name, 
                   functions_scanned, vulnerabilities_found, highest_risk_score
            FROM scan_history
            ORDER BY created_at DESC
        """).fetchall()
        
        scans = []
        for row in result:
            scans.append({
                "id": row[0],
                "created_at": row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else "",
                "scan_type": row[2],
                "target_name": row[3],
                "functions_scanned": row[4],
                "vulnerabilities_found": row[5],
                "highest_risk_score": round(row[6], 4)
            })
        return scans
    finally:
        conn.close()

def get_scan(scan_id: str):
    conn = get_connection()
    try:
        result = conn.execute("""
            SELECT report_data FROM scan_history WHERE id = ?
        """, (scan_id,)).fetchone()
        
        if result and result[0]:
            return json.loads(result[0])
        return None
    finally:
        conn.close()