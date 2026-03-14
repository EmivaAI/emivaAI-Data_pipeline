import sqlite3
import json

db_path = r'c:\Users\G.Rajesh\.gemini\antigravity\scratch\emiva-ingestion\ingestion.db'

def view_data():
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM raw_webhook_data ORDER BY received_at DESC LIMIT 10")
        rows = cur.fetchall()
        
        if not rows:
            print("No data found in raw_webhook_data table.")
            return

        print(f"{'ID':<5} | {'Source':<10} | {'Event Type':<15} | {'Received At':<25}")
        print("-" * 60)
        
        for row in rows:
            print(f"{row['id']:<5} | {row['source']:<10} | {str(row['event_type']):<15} | {row['received_at']:<25}")
            # print(f"Payload: {row['payload']}\n")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_data()
