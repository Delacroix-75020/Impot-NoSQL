from googleapiclient.discovery import build
from datetime import datetime
import json

video_info = []

DEVELOPER_KEY = "AIzaSyDr5k6Mknbj1-2RuuptNKCqocBBl3MXjHA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

next_page_token = None

# Récupérer les informations sur les vidéos publiées en 2020
while len(video_info) < 100000:
    videos_response = youtube.search().list(
        part="id,snippet",
        q="",
        type="video",
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    # Afficher les informations sur les vidéos
    for video in videos_response["items"]:
        video_response = youtube.videos().list(
            part="id,snippet,statistics",
            id=video["id"]["videoId"]
        ).execute()
        video_info.append(video_response)

        if len(video_info) >= 100000:
            break

    if "nextPageToken" in videos_response:
        next_page_token = videos_response["nextPageToken"]
    else:
        break

with open('youtube_test.json', 'w') as f:
    json.dump(video_info, f)

from IPython.display import FileLink
FileLink('youtube_test.json')

# from pprint import pprint as pp
# import pymongo
# from pymongo import MongoClient
# import json
# import pandas as pd

# client = MongoClient('mongodb+srv://YoutubeProject:ZG0maZsnyOhwg17C@clusteryoutube.q2sqkef.mongodb.net/test')
# db = client['Youtube']
# db.video = db['Video']
# print(db.video.find_one())

# test = list(db.video.aggregate([
#     {
#          "$group":{ "_id": "null", "avgViews": { "$avg": "$items.snippet.statistics.viewCount" }}
#     }
# ]))
# test = list(db.videos.aggregate([
#   { "$group": { "_id": "null", "avgViewCount": { "$avg": "$items.snippet.statistics.viewCount" } } }
# ]))
# print(test)

# unwind_ = { "$unwind": "$items.statistics.likeCount" },
# group_ = {"$group":{"_id":"$items.snippet.channelTitle", "max":{"$max": "$items.statistics.likeCount"}}}
# sort_ = {"$sort":{"max":-1}}
# limit = { "$limit": 10 }
# tab = pd.DataFrame(db.video.aggregate([ unwind_, group_, sort_, limit]))
# print(tab)


