import pandas as pd
import json
from googleapiclient.discovery import build
from datetime import datetime,date
import time
import math
import re
from comments import comments_analysis


## Global Variables
api_key = "AIzaSyCyg5iPimg6ngPOLuh1uppUtdPDOLfiCBg"


def main(mainURL="https://www.youtube.com/watch?v=xrUgURj-vFk"):
    url = mainURL
    youtube = get_youtube(api_key=api_key)
    single_video_id = transform_url(url=url)
    channel_id = get_channel_id(url_id= single_video_id, youtube= youtube)
    uploadID, main_stats = upload_id(channel_id=channel_id, youtube= youtube)
    num = size_of_loop(videos_on_channel= main_stats, number_of_videos=1000)
    videoIDS = get_videos_from_playlist(upload_id=uploadID, num= num, youtube=youtube, all_videos = False)
    list_of_lists = fifty_elements(ids_from_videos= videoIDS)
    stats= stats_from_videos(videos_list=list_of_lists, youtube=youtube) 
    objectOne = top_videos(df=stats)
    objectTwo = get_stats(dataf= stats)
    objectThree = charts(df = stats)
    objectFour = trend_top(df=stats)
    comments = comments_analysis(videoID= objectOne["most_views"]["id"])

    data = {
        "0":objectOne,
        "1": objectTwo,
        "2": objectThree,
        "3": objectFour,
        "4": stats.head(50).fillna(0).transpose().to_dict(),
        "5": main_stats,
        "6": comments
    }

    channel_name = main_stats["channel_name"].replace(" ","_")
    stats.to_csv(f"./testdata/{channel_name}.csv")

    return data


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

## The ChannelID gives us direct access to the the main stats of the channel.
## In addition to that, we can also get the ID of the 'Upload' Playlist
## This playlist contains every video that the channel has ever published.
## By having this videos, we can extract the videoID from them and get stats.

def upload_id(channel_id, youtube):
    """
    INPUT: channelID and the youtube class.
    OUTPUT 1: Upload Playlist ID
    OUTPUT 2: An object with the main stats from the channel.
    """
    upload_query = youtube.channels().list(
        part=["statistics", "snippet", "contentDetails"],
        id= channel_id).execute()
    
    upload_id= upload_query["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    main_stats = {
        "channel_name":upload_query["items"][0]["snippet"]["title"],
        "country":upload_query["items"][0]["snippet"].get("country"),
        "channel_main_stats": upload_query["items"][0]["statistics"]}

    return [upload_id], main_stats

## We are going to use a function called 'allIDS' to get all the videoID's from the channel.
## We can retrieve 50 videos per API call, so we need to caluclate how many times to run it. 
def size_of_loop(videos_on_channel, number_of_videos=1000):
    """
    INPUT: Amount of videos published by the channel.
    OUTPUT: How many times the 'allIDS' function needs to run to get all of the videoIDS. 
    If the channel has more than a 1,000 videos, the function returns 20. (1000/50) = 20.
    """
    num = 0
    
    videos_on_channel = int(videos_on_channel["channel_main_stats"]["videoCount"])

    if videos_on_channel > number_of_videos:
        num = math.floor(number_of_videos/50)
    else:
        num = math.floor(int(videos_on_channel)/50)

    if num == 0:
        num = 1
    
    return num


##  This function creates a list with all the videoIDS of a channel.
##  By default, the function returns the last 1,000 videos of a channel.
def get_videos_from_playlist(upload_id, num, youtube, all_videos = False):
    """
    INPUT: The uploadID, the youtube class, and the number of times the loop should run.
    OUTPUT: All the video id's of the channel.
    
    NOTES: By default, the max amount of videos that this function can return, by default, is 1,000. 
    If the 'all_videos' parameter is changed to 'True' the function will return every video. 
    """
    #This token especifies the list of videos we need.
    nextPageToken = None
    
    # Name of the dictionary
    videos=[]

    if all_videos == False:
        for i in range(num):
            q= youtube.playlistItems().list(
                part="contentDetails",
                playlistId=upload_id[0],
                maxResults=50,
                pageToken= nextPageToken)

            query = q.execute()
            
            for item in query["items"]:
                videos.append(item["contentDetails"]["videoId"])

            nextPageToken = query.get("nextPageToken")
    
    else:
        while True:
            q= youtube.playlistItems().list(
                part="contentDetails",
                playlistId=upload_id[0],
                maxResults=50,
                pageToken= nextPageToken)

            query = q.execute()
            
            for item in query["items"]:
                videos.append(item["contentDetails"]["videoId"])

            nextPageToken = query.get("nextPageToken")

            if not nextPageToken:
                break
        
    return videos


## This function creates a list of lists. 
def fifty_elements(ids_from_videos):
    """
    INPUT: A list with all the videoIDS of a channel.
    OUTPUT: A list that includes lists with 50 elements. 

    NOTES: This output is going to be used in the 'stats_from_video' function.
    """

    first50 = list(ids_from_videos)
    empty_list = []
    count = len(first50)

    while count > 0:
        var1 = count - 50
        var2 = count

        if var1 < 0:
            var1 = 0

        empty_list.append(first50[var1:var2])

        count -= 50

    return empty_list


## This function returns the main stats from all the videos of a Youtube Channel.
def stats_from_videos(videos_list, youtube):
    """
    INPUT: List of Youtube ID's and the youtube class.
    OUTPUT 1: A dataframe with all the stats from the videos specified on the list.
    OUTPUT 2: A dataframe with the information of the last 50 videos.
    """
    stats_dict = []

    for i in range(len(videos_list)):
        vid_request = youtube.videos().list(
            part=["snippet", "statistics", "contentDetails"],
            id=",".join(videos_list[i]))
        b = vid_request.execute()

        for si in range(len(b["items"])):
            bstats = b["items"][si]["statistics"]
            binfo = b["items"][si]["snippet"]
            bid = b["items"][si]["id"]
            bcontent = b["items"][si]["contentDetails"]
            time = bcontent.get("duration")
            
            hours = re.findall(r"(\d+)H", time)
            seconds = re.findall(r"(\d+)S", time)

            try:
                minutes = re.findall(r"(\d+)M", time)
            except TypeError:
                minutes = 0

            if not hours:
                hours = 0
            else:
                hours = int(re.findall(r"(\d+)H", time)[0])*60

            if not minutes:
                minutes = 0
            else:
                minutes = int(re.findall(r"(\d+)M", time)[0])

            if not seconds:
                seconds = 0
            else:
                seconds = int(re.findall(r"(\d+)S", time)[0])/60

            totalT = round(seconds + hours + minutes,2)
            
            stats_dict.append({
                "channel_id": binfo.get("channelId"),
                "video_id": bid,
                "publishedAt": binfo.get("publishedAt"),
                "title": binfo["title"],
                f"viewCount": bstats.get("viewCount"),
                f"likeCount": bstats.get("likeCount"),
                f"dislikeCount": bstats.get("dislikeCount"),
                f"commentCount": bstats.get("commentCount"),
                "duration": totalT,
                "thumbnail": binfo["thumbnails"]["medium"]["url"],
                "link": f"https://youtu.be/{bid}",
                "video_lang": binfo.get("defaultAudioLanguage"),
                "categoryId": binfo.get("categoryId"),
                "description": binfo.get("description")
            })

    vid_stats = pd.DataFrame.from_dict(stats_dict).sort_values(by="publishedAt", ascending=False)
    vid_stats["medianViews"] = vid_stats.viewCount.median()
    vid_stats["medianLikes"] = vid_stats.likeCount.median()
    vid_stats["medianComments"] = vid_stats.commentCount.median()
    vid_stats["medianDislikeCount"] = vid_stats.dislikeCount.median()
    

    return vid_stats 


def top_videos(df):
    mostViews= df.sort_values(by=["viewCount"], ascending=False).iloc[0:1,:]
    lessViews = df.sort_values(by=["viewCount"]).iloc[0:1,:]
    mostRecent = df.head(1)
    most_views = {
        "most_views":{
            "title" : mostViews["title"].tolist()[0],
            "publishedAt": mostViews["publishedAt"].tolist()[0],
            "viewCount": mostViews["viewCount"].tolist()[0],
            "likeCount": mostViews["likeCount"].tolist()[0],
            "dislikeCount": mostViews["dislikeCount"].tolist()[0],
            "commentCount" : mostViews["commentCount"].tolist()[0],
            "thumbnail" : mostViews["thumbnail"].tolist()[0],
            "link" : mostViews["link"].tolist()[0],
            "id": mostViews["video_id"].tolist()[0]
            },
        "less_views":{
            "title": lessViews["title"].tolist()[0],
            "publishedAt": lessViews["publishedAt"].tolist()[0],
            "viewCount": lessViews["viewCount"].tolist()[0],
            "likeCount": lessViews["likeCount"].tolist()[0],
            "dislikeCount": lessViews["dislikeCount"].tolist()[0],
            "commentCount" : lessViews["commentCount"].tolist()[0],
            "thumbnail" : lessViews["thumbnail"].tolist()[0],
            "link" : lessViews["link"].tolist()[0],
            "id": lessViews["video_id"].tolist()[0]
            },
        "most_recent":{
            "title": mostRecent["title"].tolist()[0],
            "publishedAt": mostRecent["publishedAt"].tolist()[0],
            "viewCount": mostRecent["viewCount"].tolist()[0],
            "likeCount": mostRecent["likeCount"].tolist()[0],
            "dislikeCount": mostRecent["dislikeCount"].tolist()[0],
            "commentCount" : mostRecent["commentCount"].tolist()[0],
            "thumbnail" : mostRecent["thumbnail"].tolist()[0],
            "link" : mostRecent["link"].tolist()[0],
            "id": mostRecent["video_id"].tolist()[0]
            }
    }
    return most_views


def get_stats(dataf):

    videoStats = {
        "dislikes" : int(dataf.dislikeCount.fillna(0).astype('int32').sum()),
        "likes" : int(dataf.likeCount.fillna(0).astype('int32').sum()),
        "comments" : int(dataf.commentCount.fillna(0).astype('int32').sum()),
        "total_time" : int(dataf.duration.fillna(0).astype('int32').sum())/60,
    }

    return videoStats


def charts(df):
    df = df[0:50]
    charts = {
        "views": df.viewCount.astype("int32").to_list(),
        "dates" : df.publishedAt.to_list(),
        "title": df.title.to_list(),
        "link": df.link.to_list(),
        "thumbnail": df.thumbnail.to_list(),
        "comments" : df.commentCount.astype("int32").to_list(),
        "dislikes" : df.dislikeCount.astype("int32").to_list()
    }
    return charts


def trend_top(df):

    empty = []
    topVideo = int(df.sort_values(by=["viewCount"], ascending=False).iloc[0:1,:].index[0])
    
    for i in range(11):
        index = topVideo-5
        empty.append(df.loc[df.index == index+i ])
    
    dataframe = pd.concat(empty)

    charts = {
        "views": dataframe.viewCount.astype("int32").to_list(),
        "dates" : dataframe.publishedAt.to_list(),
        "title": dataframe.title.to_list(),
        "link": dataframe.link.to_list(),
        "thumbnail": dataframe.thumbnail.to_list()
    }
    return charts


if __name__ == "__main__":
    # execute only if run as a script
    main()