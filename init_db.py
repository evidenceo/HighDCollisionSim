import sqlite3

conn = sqlite3.connect('../HighDCollisionSimulation/vehicle_risk_scores.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS risk_scores
             (vehicle_id TEXT PRIMARY KEY, risk_score TEXT)''')

conn.commit()
conn.close()
