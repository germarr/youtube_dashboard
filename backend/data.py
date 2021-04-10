import pandas as pd
import json
from googleapiclient.discovery import build
from datetime import datetime,date
import time
import math

## Global Variables
api_key = "AIzaSyCyg5iPimg6ngPOLuh1uppUtdPDOLfiCBg"
url ="https://www.youtube.com/watch?v=xrUgURj-vFk"

def main():
    youtube = get_youtube(api_key=api_key)
    single_video_id = transform_url(url=url)
    channel_id = get_channel_id(url_id= single_video_id, youtube= youtube)


## This functions returns the 'Youtube' class.
## This class contains all the functions necessary to interact with the Youtube API.
def get_youtube(api_key):
    """ 
    INPUT: Google API Key.
    OUTPUT: Class with all the functions necessary to interact with the Youtube API.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    
    return youtube

## To get the main stats from a Youtube channel, using the URL of any of the channel's video, we need a videoID.
def transform_url(url):
    """
    INPUT: URL of any Youtube video.
    OUTPUT: A videoID. Necessary to get the data from the channel.
    """
    single_video_id = url.split("=")[1].split("&")[0]
    return single_video_id

## Once we got the videoID we can use it to get the channelID.
def get_channel_id(url_id, youtube):
    """
    INPUT: videoID and the 'youtube' class.
    OUPUT: The channelID
    """
    channel_id_query = youtube.videos().list(
        part=["snippet", "statistics", "contentDetails"],
        id=url_id).execute()

    channel_id = channel_id_query["items"][0]["snippet"]["channelId"]
    
    return channel_id


