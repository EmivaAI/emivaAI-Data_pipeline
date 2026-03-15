import sqlite3
import json
from config import config

def view_data():
    try:
        # Extract file path from sqlite:/// URL
        db_path = config.DATABASE_URL.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check if table exists first
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw_webhook_data'")
        if not cur.fetchone():
            print("Table 'raw_webhook_data' does not exist yet. Send some webhooks first!")
            return

        cur.execute("SELECT * FROM raw_webhook_data ORDER BY id DESC LIMIT 20")
        rows = cur.fetchall()
        
        if not rows:
            print("No data found in raw_webhook_data table.")
            return

        print(f"{'ID':<5} | {'Source':<10} | {'Event Type':<20} | {'Received At':<25}")
        print("-" * 70)
        
        for row in rows:
            received_at = str(row['received_at'])
            event_type = str(row['event_type']) if row['event_type'] else 'N/A'
            print(f"{row['id']:<5} | {row['source']:<10} | {event_type:<20} | {received_at:<25}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    view_data()
