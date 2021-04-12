import pandas as pd
from googleapiclient.discovery import build
from transformers import pipeline
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification


def comments_analysis(videoID):
    api_key = "AIzaSyCyg5iPimg6ngPOLuh1uppUtdPDOLfiCBg"
    youtube = get_youtube(api_key = api_key)
    comments_list, comments_df = get_comments(vid_id=videoID ,youtube=youtube, number = 10)
    df = classify_comments(list_of_comments=comments_list)
    return df

def get_youtube(api_key):
    """ 
    INPUT: Google API Key.
    OUTPUT: Class with all the functions necessary to interact with the Youtube API.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    
    return youtube

def get_comments(vid_id,youtube, number = 5):
    nextPageToken = None
    comments_list=[]
    
    for si in range(number):
        query= youtube.commentThreads().list(part=["snippet","replies"],
                                                videoId=vid_id, 
                                                maxResults=50,
                                                pageToken= nextPageToken)
        comments_query = query.execute()

        loop = len(comments_query["items"])

        for comment in range(loop):
            comments_list.append(
                comments_query["items"][comment]["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            )

        nextPageToken = comments_query.get("nextPageToken")
        
        if not nextPageToken:
            break

    comments_df = pd.DataFrame.from_dict(comments_list)
    comments_df.to_csv(f"./testdata/test_comments.csv")

    return comments_list

def classify_comments(list_of_comments): 
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    model = TFAutoModelForSequenceClassification.from_pretrained(model_name, from_pt=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    classifier = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
    e_list = []

    comments = list_of_comments

    for i in range(len(comments)):
        data = classifier(comments[i])[0]
        e_list.append({
            "score" : data["score"],
            "stars": data["label"]
        })

    df = pd.DataFrame.from_dict(e_list)
    df.to_csv("./testdata/sentiment_analysis.csv")
    dfv2 = df.groupby("stars").size().reset_index().set_index("stars").transpose().to_dict()

    return dfv2


if __name__ == "__main__":
    # execute only if run as a script
    comments_analysis()