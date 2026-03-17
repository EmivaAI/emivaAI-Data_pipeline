import sqlite3
import json
from config import config

def view_changes():
    try:
        db_path = config.DATABASE_URL.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='change_event'")
        if not cur.fetchone():
            print("Table 'change_event' does not exist yet. Run the processor first!")
            return

        cur.execute("SELECT * FROM change_event ORDER BY timestamp DESC")
        rows = cur.fetchall()
        
        if not rows:
            print("No consolidated changes found.")
            return

        print(f"{'ID':<3} | {'Type':<10} | {'Component':<15} | {'Issues':<15} | {'Actors':<20} | {'Summary':<30}")
        print("-" * 105)
        
        for row in rows:
            issues = ", ".join(json.loads(row['linked_issues'])) if row['linked_issues'] else 'N/A'
            actors = ", ".join(json.loads(row['actors'])) if row['actors'] else 'N/A'
            print(f"{row['id']:<3} | {row['change_type']:<10} | {row['component']:<15} | {issues:<15} | {actors:<20} | {row['summary'][:30]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    view_changes()
