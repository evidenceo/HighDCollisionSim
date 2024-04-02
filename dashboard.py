import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

app = dash.Dash(__name__)

# Define app layout with three Graph components
app.layout = html.Div([
    html.H1("Vehicle Collision Risk Dashboard"),
    dcc.Interval(id="interval-update", interval=1000, n_intervals=0),
    dcc.Graph(id="real-time-risk-chart"),
    dcc.Graph(id="high-risk-alerts-chart"),
    dcc.Graph(id="risk-score-distribution-chart"),
])

# Callback for real-time risk classification chart
@app.callback(
    Output("real-time-risk-chart", "figure"),
    [Input("interval-update", "n_intervals")]
)
def update_real_time_risk_chart(_):
    conn = sqlite3.connect('vehicle_risk_scores.db')
    # Query to fetch the latest risk scores
    df = pd.read_sql_query("SELECT vehicle_id, risk_score FROM risk_scores ORDER BY last_updated DESC", conn)
    conn.close()

    # Map risk scores to colors
    color_map = {
        'Low Risk - Normal driving behaviour': 'green',
        'Moderate Risk - Caution advised': 'orange',
        'High Risk - Immediate action required': 'red'
    }
    df['color'] = df['risk_score'].map(color_map)

    # Generate the bar chart
    fig = px.bar(df, x='vehicle_id', y='risk_score',
                 color='color',
                 color_discrete_map="identity",
                 title="Real-Time Risk Classification",
                 labels={'risk_score': 'Risk Score', 'vehicle_id': 'Vehicle ID'},
                 height=400)

    # Customize layout for better readability
    fig.update_layout(xaxis_title="Vehicle ID",
                      yaxis_title="Risk Score",
                      legend_title="Risk Score")
    fig.update_traces(marker_line_color='rgb(8,48,107)',
                      marker_line_width=1.5, opacity=0.6)

    return fig


# Callback for high-risk alerts chart
@app.callback(
    Output("high-risk-alerts-chart", "figure"),
    [Input("interval-update", "n_intervals")]
)
def update_high_risk_alerts_chart(_):
    conn = sqlite3.connect('vehicle_risk_scores.db')  # Adjust the path as necessary
    # Query to fetch only high-risk vehicles
    df = pd.read_sql_query("SELECT vehicle_id, risk_score FROM risk_scores WHERE risk_score = 'High Risk - Immediate action required' ORDER BY last_updated DESC", conn)
    conn.close()

    # Check if dataframe is empty
    if df.empty:
        fig = px.scatter(title="No High Risk Vehicles Detected")
        fig.update_layout(xaxis=dict(showgrid=False, zeroline=False, visible=False),
                          yaxis=dict(showgrid=False, zeroline=False, visible=False))
        return fig

    # Generate the scatter plot
    fig = px.scatter(df, x='vehicle_id', y=[1] * len(df),  # Using a dummy y-axis value to align horizontally
                     text='vehicle_id', size_max=60, color_discrete_sequence=['red'],
                     title="High Risk Vehicle Alerts",
                     labels={'vehicle_id': 'Vehicle ID'},
                     height=400)

    # Customize layout for better readability
    fig.update_layout(xaxis_title="Vehicle ID",
                      yaxis_title="",
                      yaxis=dict(showgrid=False, zeroline=False, visible=False),
                      showlegend=False)
    fig.update_traces(textposition='top center')

    return fig

# Callback for risk score distribution chart
@app.callback(
    Output("risk-score-distribution-chart", "figure"),
    [Input("interval-update", "n_intervals")]
)
def update_risk_score_distribution_chart(_):
    conn = sqlite3.connect('vehicle_risk_scores.db')  # Adjust the path as necessary
    # Query to fetch all risk scores
    df = pd.read_sql_query("SELECT risk_score, COUNT(vehicle_id) AS count FROM risk_scores GROUP BY risk_score ORDER BY CASE risk_score WHEN 'High Risk - Immediate action required' THEN 1 WHEN 'Moderate Risk - Caution advised' THEN 2 ELSE 3 END", conn)
    conn.close()

    # Check if dataframe is empty
    if df.empty:
        fig = px.histogram(title="No Risk Score Data Available")
        fig.update_layout(xaxis=dict(showgrid=False, zeroline=False, visible=False),
                          yaxis=dict(showgrid=False, zeroline=False, visible=False))
        return fig

    # Generate the histogram
    fig = px.histogram(df, x='risk_score', y='count',
                       title="Risk Score Distribution",
                       labels={'count': 'Number of Vehicles', 'risk_score': 'Risk Score'},
                       color='risk_score',
                       color_discrete_map={
                           'High Risk - Immediate action required': 'red',
                           'Moderate Risk - Caution advised': 'orange',
                           'Low Risk - Normal driving behaviour': 'green'
                       },
                       height=400)

    # Customize layout for better readability
    fig.update_layout(xaxis_title="Risk Score",
                      yaxis_title="Number of Vehicles",
                      bargap=0.2)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
