'''
Youtube free tier quota = 10k units per day

For content-experts, extract youtube video:
- title
- comments (with likes)
- likes
- views
- transcript if available
'''

from dotenv import load_dotenv
import os
import googleapiclient.discovery
import sqlite3
import base64
import os
import spacy
import logging
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

load_dotenv()

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('logs/youtube_extract.log', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

class YoutubeExtractor:
    def __init__(self, topic_list, languages=['en']):
        self.topic_list = topic_list
        self.languages = languages
        self.comments_next_page_token = None
        api_service_name = "youtube"
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.salt = os.getenv('SALT')
        api_version = "v3"
        self.youtube_client = googleapiclient.discovery.build(
            api_service_name,
            api_version, 
            developerKey = os.getenv('YOUTUBE_API_KEY')
        )
        self.database_path = os.path.join("data", os.getenv('SQLITE_DB_NAME'))
        self.create_comments_table()
        self.logger = setup_custom_logger('youtube_extract')

        # init encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes(self.salt, 'utf-8'),
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(bytes(self.encryption_key, 'utf-8')))
        self.fernet = Fernet(key)

        # init spacy
        self.nlp = spacy.load("en_core_web_sm")


    def create_comments_table(self):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS comments (
            video_id text,
            channel_id text,
            comment_id text,
            comment_text text,
            comment_likes integer,
            comment_author_channel_id text,
            comment_published_at text,
            comment_updated_at text,
            is_reply boolean,
            reply_by_channel_owner boolean,
            load_ts DEFAULT CURRENT_TIMESTAMP,
            to_classify boolean
        )''')
        conn.commit()
        conn.close()

    def get_video_stats(self, video_id):
        request = self.youtube_client.videos().list(
            part="contentDetails,topicDetails,snippet,statistics",
            id=video_id
        )
        response = request.execute()
        print(response)

    def get_all_comment_threads(self, object_id, object_type='channel'):
        iter = 0
        total_count = 0
        self.logger.info(f"object_id: {object_id}, object_type: {object_type}")
        try:
            while self.comments_next_page_token or iter == 0:
                response = self.get_comment_threads(object_id, object_type=object_type)
                page_count = response['pageInfo']['totalResults']
                total_count += page_count
                for item in response['items']:
                    self.save_comment(self.extract_comment(item['snippet']['topLevelComment']))
                    if item.get('replies', None):
                        for reply in item['replies']['comments']:
                            reply = self.extract_comment(reply, is_reply=True)
                            self.save_comment(reply)
                self.logger.info(f'Iteration: {iter}, Page count: {page_count}, Total count: {total_count}')
                iter += 1
        except Exception as e:
            self.logger.error(e)
            return None

    def get_comment_threads(self, object_id, object_type='channel'):
        """quote = 10 units per request"""
        if object_type == 'channel':
            request = self.youtube_client.commentThreads().list(
                part="id,snippet,replies",
                allThreadsRelatedToChannelId=object_id,
                maxResults=100,
                textFormat="plainText",
                pageToken=self.comments_next_page_token
            )
        elif object_type == 'video':
            request = self.youtube_client.commentThreads().list(
                part="id,snippet,replies",
                maxResults=100,
                textFormat="plainText",
                videoId=object_id,
                pageToken=self.comments_next_page_token
            )
        response = request.execute()
        self.comments_next_page_token = response.get('nextPageToken', None)
        return response

    def save_comment(self, comment_tuple):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        c.execute("""INSERT INTO comments 
            (
                video_id,
                channel_id,
                comment_id,
                comment_text,
                comment_likes,
                comment_author_channel_id,
                comment_published_at,
                comment_updated_at,
                is_reply,
                reply_by_channel_owner
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)""", comment_tuple)
        conn.commit()
        conn.close()

    def get_closed_captions(self):
        """no longer accessible via data api without authentication by the channel owner"""
        # https://issuetracker.google.com/issues/241669016?pli=1
        pass

    def extract_comment(self, comment_dict, is_reply=False):
        '''Transform comment dictionary into a tuple'''
        video_id = self.fernet.encrypt(bytes(comment_dict['snippet']['videoId'], 'utf-8')).decode('utf-8')
        channel_id = self.fernet.encrypt(bytes(comment_dict['snippet']['channelId'], 'utf-8')).decode('utf-8') if comment_dict.get('snippet').get('channelId', None) else None
        comment_id = self.fernet.encrypt(bytes(comment_dict['id'], 'utf-8')).decode('utf-8')
        comment_text = self.redact_names(comment_dict['snippet']['textDisplay'])
        comment_likes = comment_dict['snippet']['likeCount']
        #comment_author = self.fernet.encrypt(bytes(comment_dict['snippet']['authorDisplayName'], 'utf-8')).decode('utf-8')
        comment_author_channel_id = self.fernet.encrypt(bytes(comment_dict['snippet']['authorChannelId']['value'], 'utf-8')).decode('utf-8') if comment_dict['snippet'].get('authorChannelId', None) else None
        comment_published_at = comment_dict['snippet']['publishedAt']
        comment_updated_at = comment_dict['snippet']['updatedAt']
        reply_by_channel_owner = True if is_reply and channel_id == comment_author_channel_id else False
        return (video_id, channel_id, comment_id, comment_text, comment_likes, comment_author_channel_id, comment_published_at, comment_updated_at, is_reply, reply_by_channel_owner)
    
    def redact_names(self, comment_text):
        """Remove names from comment text"""
        doc = self.nlp(comment_text)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                replace_text = ent.text
                if len(ent.text) > 2:
                    # preserve possessives
                    if ent.text[-2:] == "'s":
                        replace_text = ent.text[:-2]
                    elif ent.text[-1:] == "'": 
                        replace_text = ent.text[:-1]
                comment_text = comment_text.replace(replace_text, 'PERSON')
        return comment_text

    def find_experts(self, topic_list, language='en'):
        """This was too cumbersome, went with a convenience sample...

        Search by topic list
        Verify keywords in channel description
        Check that channel thumbnail is a person's face
        """
        pass
      
                
def main():
    extractor = YoutubeExtractor([])
    with open("data/channels_en.txt", "r") as f:
         channels = f.read().splitlines()
         for channel in channels:
             channel_id = channel.split("|")[1]
             extractor.get_all_comment_threads(channel_id, object_type='channel')
    
    with open("data/vids_to_search_dedup_en.txt", "r") as f:
        videos = f.read().splitlines()
        for video_id in videos:
            extractor.get_all_comment_threads(video_id, object_type='video')

    conn = sqlite3.connect(extractor.database_path)
    conn.execute("""
        -- Dedup due to inclusion of channel and video
        DELETE FROM comments
        WHERE rowid NOT IN (
        SELECT MIN(rowid) 
        FROM comments
        GROUP BY comment_id
    """)

if __name__ == "__main__":
    main()
