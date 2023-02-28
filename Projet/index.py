import time
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from dash.exceptions import PreventUpdate
from dash import Input, Output, dcc, html
from app import app

weather_path="C:/Users/ppep/Documents/csv_proj/weather.csv"
airlines_path="C:/Users/ppep/Documents/csv_proj/airlines.csv"
airports_path="C:/Users/ppep/Documents/csv_proj/airports.csv"
flights_path="C:/Users/ppep/Documents/csv_proj/flights.csv"
planes_path="C:/Users/ppep/Documents/csv_proj/planes.csv"

df_data_planes = pd.read_csv(planes_path)
df_data_airlines= pd.read_csv(airlines_path)
df_data_weather=pd.read_csv(weather_path)
df_data_airports=pd.read_csv(airports_path)
df_data_flights=pd.read_csv(flights_path)

app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Wep App"),
        dcc.Interval(
        id="load_interval", 
        n_intervals=0, 
        max_intervals=0,
        interval=1
        ),
        html.Hr(),
        dcc.Graph(id="graph1"),
        dcc.Graph(id="graph2"),
        dcc.Graph(id="graph3"),
        html.Div(id="tab-content", className="p-4"),
    ]
)
@app.callback(
    Output("graph1","figure"),
    Output("graph2","figure"),
    Output("graph3","figure"),
    Input("load_interval","n_intervals")
)
def display_graph(n):

  a = df_data_airlines['name'].shape[0]
  b = df_data_airports['name'].shape[0]
  c = df_data_flights.air_time.value_counts(dropna=False)[0]

  name_list_dataframe_1 = ["nombre_de_compagnie", "nombre_d'avion", "nombre_de_vol_annulé"]
  value_list_dataframe_1 = [a,b,c]

  dataframe_first_list = {"value":value_list_dataframe_1 ,"name": name_list_dataframe_1}

  dataframe_1 = pd.DataFrame(dataframe_first_list)
  dataframe_2 = df_data_flights.groupby(['carrier'])['dest'].count().sort_values(ascending=False).reset_index(name="y")
  dataframe_3 = df_data_flights.groupby(['origin', 'carrier'])['dest'].count().sort_values(ascending=False).reset_index(name="y")
  dataframe_3["Aéroport + Compagnie"] = dataframe_3["origin"] + " " + dataframe_3["carrier"]
  fig1 = px.pie(dataframe_1, values='value', names='name', title="Statistique Générale")
  fig2 = px.bar(dataframe_2, x="carrier", y="y", title="Nombre désservie par compagnie dans des aéroports")
  fig3 = px.bar(dataframe_3, x="Aéroport + Compagnie", y="y", title="Nombre désservie par compagnie par aéroport d'origine")

  return fig1, fig2, fig3

if __name__ == '__main__':
    app.run_server(debug=True, port=5560, use_reloader=False)
