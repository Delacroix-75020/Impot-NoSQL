import pandas as pd
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import nltk
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from dash import dash_table
from pymongo import MongoClient
from dash.exceptions import PreventUpdate
from dash import Input, Output, dcc, html
from app import app

# Import the stop words for English and French
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

# Connect to MongoDB
client = MongoClient('mongodb+srv://YoutubeProject:ZG0maZsnyOhwg17C@clusteryoutube.q2sqkef.mongodb.net/test')
db = client['Youtube']
collection = db['Video']# Define stopwords for both French and English languages
collection_channel = db['Channel']# Define stopwords for both French and English languages

def word_frequence():

    key_list_01 = []
    value_list_01 = []

    stopwords_fr = set(stopwords.words('french'))
    stopwords_en = set(stopwords.words('english'))# Retrieve the 'description' field for each document in the collection
    descriptions = [doc['items'][0]['snippet']['title'] for doc in collection.find()]# Tokenize the descriptions into words, filter out stop words and punctuation marks, and count the frequency of each word
    all_words = []
    for desc in descriptions:
        words = [word.lower() for word in word_tokenize(desc) if word.lower() not in stopwords_fr and word.lower() not in stopwords_en and word.isalnum()]
        words = [re.sub(r'\d+', '', word) for word in words] # remove numbers
        all_words.extend(words)
    word_freq = Counter(all_words)# Sort the words in descending order based on their frequency
    # Filter out any words that consist only of whitespace characters (such as spaces)
    word_freq = {k: v for k, v in word_freq.items() if k.strip()}
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)# Print the top 10 most frequent words
    n = 10
    for key, value in sorted_words[:n]:
        key_list_01.append(key)
        value_list_01.append(value)

    df = pd.DataFrame({"Mots les plus utilisés dans les titres": key_list_01, "Nombre de mots fois utilisés": value_list_01})

    return df

def most_tag_used():
    documents = collection.find({'items.snippet.tags': {'$exists': True}})# Count the occurrences of each tag
    tag_counts = {}
    for document in documents:
        tags = document['items'][0]['snippet']['tags']
        for tag in tags:
            if tag in tag_counts:
                tag_counts[tag] += 1
            else:
                tag_counts[tag] = 1 # Create a DataFrame with the tag counts
    df = pd.DataFrame.from_dict(tag_counts, orient='index', columns=['Nombre de tag utilisé'])
    df.index.name = 'Les tags les plus fréquents'# Sort the DataFrame by tag count in descending order
    df = df.sort_values('Nombre de tag utilisé', ascending=False)# Print the top 10 tags
    df = df.reset_index()
    df.head(10)

    return df.head(10)

def most_watched_video():

    # Agrégation par "items.snippet.title" et récupération de la valeur maximale de "items.statistics.viewCount" pour chaque groupe
    pipeline = [
        {"$group": {"_id": "$items.snippet.title", "viewCount": {"$max": "$items.statistics.viewCount"}}},
        {"$sort": {"viewCount": -1}},
        {"$limit": 10}
    ]
    cursor = collection.aggregate(pipeline)

    # Conversion des résultats en DataFrame et extraction des valeurs des listes dans les colonnes
    df = pd.DataFrame(list(cursor))
    df = df.rename(columns={"_id": "Titre des vidéos les plus vues", "viewCount":"Nombre de vue"})
    df['Titre des vidéos les plus vues'] = df['Titre des vidéos les plus vues'].apply(lambda x: x[0])
    df['Nombre de vue'] = df['Nombre de vue'].apply(lambda x: x[0])

    return df

def most_liked_video():
    # Exécution de la requête
    cursor = collection.find({}, {"_id": 0, "items.snippet.title": 1, "items.statistics.likeCount": 1}).sort("items.statistics.likeCount", -1).limit(10)

    # Conversion des résultats en DataFrame
    df = pd.DataFrame(list(cursor))
    #voila comment acceder aux donner
    data = []
    for i in range(9): #voila comment acceder au valeurs
        data.append([df['items'][i][0]['snippet']['title'] , df['items'][i][0]['statistics']['likeCount']])
    df = pd.DataFrame(data, columns=['Titre des vidéos les plus liker', 'Nombre de like'])
    
    return df

def most_created_video():
    # Define the aggregation pipeline
    pipeline = [
        {'$unwind': '$snippet'},
        {'$group': {'_id': '$snippet.channelTitle', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]

    # Execute the aggregation pipeline and store the results in a list of dictionaries
    results = []
    cursor = collection_channel.aggregate(pipeline)
    for channel in cursor:
        results.append({'Les chaînes qui ont le plus de vidéo': channel['_id'], 'Nombre de video': channel['count']})

    # Create a dataframe from the results list
    df = pd.DataFrame(results)

    return df

df_01 = word_frequence()
df_02 = most_tag_used()
df_03 = most_watched_video()
df_04 = most_liked_video()
df_05 = most_created_video()

print(df_03)

app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.H1("Wep App with MongoDB"),
        dcc.Interval(
            id="load_interval",
            n_intervals=0,
            max_intervals=0,
            interval=1
        ),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H4("Les Mots les plus fréquemment utilisés dans les titres"),
                dcc.Graph(id="graph1"),
            ], width=6, style={"padding": "10px", "margin": "0"}),
            dbc.Col([
                dash_table.DataTable(
                    data=df_01.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df_01.columns],
                    style_header={
                        "backgroundColor": "#667579",
                        "color": "white",
                        "textAlign": "center",
                        "border": "1px solid #3D4648"},
                    style_cell={"textAlign": "center", "border": "1px solid #3D4648"},
                ),               
            ], width=6, style={"padding": "10px", "margin-top": "100px"}),
        ], className="g-0"),
        dbc.Row([
            dbc.Col([
                html.H4("Les tags les plus fréquents"),
                dcc.Graph(id="graph2"),
                ], width=6, style={"padding": "10px", "margin": "0"}),
            dbc.Col([
                dash_table.DataTable(
                    data=df_02.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df_02.columns],
                    style_header={
                        "backgroundColor": "#667579",
                        "color": "white",
                        "textAlign": "center",
                        "border": "1px solid #3D4648"},
                    style_cell={"textAlign": "center", "border": "1px solid #3D4648"},
                )
                ], width=6, style={"padding": "10px", "margin-top": "60px"}),
        ], className="g-0"),
        dbc.Row([
            dbc.Col([
                html.H4("Les vidéos avec le plus grand nombre de vue"),
                dcc.Graph(id="graph3"),
            ], width=6, style={"padding": "10px", "margin": "0"}),
            dbc.Col([
                dash_table.DataTable(
                    data=df_03.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df_03.columns],
                    style_header={
                        "backgroundColor": "#667579",
                        "color": "white",
                        "textAlign": "center",
                        "border": "1px solid #3D4648"},
                    style_cell={"textAlign": "center", "border": "1px solid #3D4648"},
                ),               
            ], width=6, style={"padding": "10px", "margin-top": "60px"}),
        ], className="g-0"),
        dbc.Row([
            dbc.Col([
                html.H4("Titre des vidéos les plus liker"),
                dash_table.DataTable(
                    data=df_04.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df_04.columns],
                    style_header={
                        "backgroundColor": "#667579",
                        "color": "white",
                        "textAlign": "center",
                        "border": "1px solid #3D4648"},
                    style_cell={"textAlign": "center", "border": "1px solid #3D4648"},
                ),               
            ], width=12, style={"padding": "10px", "margin-top": "60px"}),
        ], className="g-0"),
        dbc.Row([
            dbc.Col([
                html.H4("Les chaînes qui ont le plus de vidéo"),
                dcc.Graph(id="graph5"),
            ], width=6, style={"padding": "10px", "margin": "0"}),
            dbc.Col([
                dash_table.DataTable(
                    data=df_05.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df_05.columns],
                    style_header={
                        "backgroundColor": "#667579",
                        "color": "white",
                        "textAlign": "center",
                        "border": "1px solid #3D4648"},
                    style_cell={"textAlign": "center", "border": "1px solid #3D4648"},
                ),               
            ], width=6, style={"padding": "10px", "margin-top": "60px"}),
        ], className="g-0"),
    ]
)

@app.callback(
    Output("graph1", "figure"),
    Output("graph2", "figure"),
    Output("graph3", "figure"),
    Output("graph5", "figure"),
    Input("load_interval", "n_intervals")
)
def display_graph(n):

    df_01 = word_frequence()
    df_02 = most_tag_used()
    df_03 = most_watched_video()
    df_05 = most_created_video()

    fig1 = px.bar(df_01, x='Mots les plus utilisés dans les titres', y='Nombre de mots fois utilisés', title="Les Mots les plus fréquemment recherchés")
    fig2 = px.bar(df_02, x="Les tags les plus fréquents", y="Nombre de tag utilisé", title="Les tags les plus fréquemment utilisés")
    fig3 = px.bar(df_03, x="Titre des vidéos les plus vues", y="Nombre de vue", title="Les vidéos avec le plus grand nombre de vue")
    fig3.update_xaxes(tickangle=45, tickfont=dict(size=10), tickmode='linear', ticktext=df_03['Titre des vidéos les plus vues'].apply(lambda x: x[:10]))
    fig5 = px.bar(df_05, x="Les chaînes qui ont le plus de vidéo", y="Nombre de video", title="Les vidéos avec le plus grand nombre de vue")
    fig5.update_xaxes(tickangle=45, tickfont=dict(size=10), tickmode='linear', ticktext=df_05['Les chaînes qui ont le plus de vidéo'].apply(lambda x: x[:10]))

    return fig1, fig2, fig3, fig5


if __name__ == '__main__':
    app.run_server(debug=True, port=5560, use_reloader=False)
