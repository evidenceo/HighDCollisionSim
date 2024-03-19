import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import sqlite3

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Vehicle Collision Risk Dashboard"),
    dcc.Interval(id="interval-update", interval=1000, n_intervals=0),
    dcc.Graph(id="risk-score-graph"),
])


@app.callback(Output("risk-score-graph", "figure"), [Input("interval-update", "n_intervals")])
def update_graph(_):
    conn = sqlite3.connect('../HighDCollisionSimulation/vehicle_risk_scores.db')
    df = pd.read_sql_query("SELECT * FROM risk_scores", conn)
    conn.close()

    # Assuming you want to display the risk scores in a bar chart
    fig = (px.bar(df, x='vehicle_id', y='risk_score', color='risk_score',
                  labels={'risk_score': 'Risk Score', 'vehicle_id': 'Vehicle ID'}))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
