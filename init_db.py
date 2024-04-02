import sqlite3

conn = sqlite3.connect('vehicle_risk_scores.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS risk_scores
             (vehicle_id TEXT PRIMARY KEY,
              risk_score TEXT,
              last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

conn.commit()
conn.close()
