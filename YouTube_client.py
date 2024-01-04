#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os

from googleapiclient.discovery import build
import pandas as pd
from IPython.display import JSON
import numpy as np
from dateutil import parser
import isodate


# In[51]:


class YouTube(object):
    api_key = None
    

    # Get credentials and create an API Client 
    def startAPI(self,api_key):
        api_service_name = "youtube"
        api_version = "v3"
        youtube = build(
            api_service_name, api_version, developerKey=api_key)
        return youtube
    # Voy a buscar las estadísticas principales del canal, 
    def get_channel_stats(self,youtube, channel_ids):
        all_data=[]
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id= ",".join(channel_ids)
        )
        response = request.execute()

        for item in response['items']:
            data = {'channelName': item['snippet']['title'],
                    'subscribers': item['statistics']['subscriberCount'],
                    'views': item['statistics']['viewCount'],
                    'totalviews': item['statistics']['videoCount'],
                    'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
                   }
            all_data.append(data)

        return(pd.DataFrame(all_data))
    
    def get_video_ids(self, youtube, playlist_ids):
        if not playlist_ids:
            print("No se encontraron IDs de playlist.")
            return []
        all_video_ids = []
        for playlist_id in playlist_ids:
            video_ids = []
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults = 50
            )
            response = request.execute()

            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')
            while next_page_token is not None:
                request = youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id,
                    maxResults = 50,
                    pageToken=next_page_token)
                response = request.execute()

                for item in response['items']:
                    video_ids.append(item['contentDetails']['videoId'])

                next_page_token = response.get('nextPageToken')

            all_video_ids.extend(video_ids)

        return all_video_ids
    
    def get_video_details(self,youtube, video_ids):
        all_video_info = []
        for i in range (0, len(video_ids),50):
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=','.join(video_ids[i:i+50])
            )
            response = request.execute()

            for video in response['items']:
                stats_to_keep = {'snippet':['channelTitle','title','description','tags','publishedAt'],
                                'statistics':['viewCount','likeCount','favouriteCount','commentCount'],
                                'contentDetails':['duration','definition','caption']}
                video_info = {}
                video_info['video_id'] = video['id']

                for k in stats_to_keep.keys():
                    for v in stats_to_keep[k]:
                        try:
                            video_info[v] = video[k][v]
                        except:
                            video_info[v] = None

                all_video_info.append(video_info)
        return pd.DataFrame(all_video_info)
    def get_comments_in_videos(self,youtube, video_ids):
        all_comments = []
        for video_id in video_ids:
            try:
                request = youtube.commentThreads().list(
                part = "snippet,replies",
                videoId = video_id
                )
                response = request.execute()

                comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items'][0:10]]
                comments_in_video_info = {'video_id': video_id, 'comments': comments_in_video}

                all_comments.append(comments_in_video_info)

            except: 
                # When error occurs - most likely because comments are disabled on a video
                print('Could not get comments for video ' + video_id)

        return pd.DataFrame(all_comments) 







