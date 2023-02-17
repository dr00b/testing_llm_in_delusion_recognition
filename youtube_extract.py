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
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

load_dotenv()

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

        # init encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes(self.salt, 'utf-8'),
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(bytes(self.encryption_key, 'utf-8')))
        self.fernet = Fernet(key)

    def create_comments_table(self):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS comments (
            video_id text,
            channel_id text,
            comment_id text,
            comment_text text,
            comment_likes integer,
            comment_author text,
            comment_author_id text,
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

    def get_video_stats(self):
        dementia_vid = 'q3NgWY-BAJw'
        request = self.youtube_client.videos().list(
            part="contentDetails,topicDetails,snippet,statistics",
            id=dementia_vid
        )
        response = request.execute()
        print(response)

    def get_all_comment_threads(self, channel_id):
        iter = 0
        total_count = 0
        while self.comments_next_page_token or iter == 0:
            response = self.get_comment_threads(channel_id)
            page_count = response['pageInfo']['totalResults']
            total_count += page_count
            for item in response['items']:
                self.save_comment(self.extract_comment(item['snippet']['topLevelComment']))
                if item.get('replies', None):
                    for reply in item['replies']['comments']:
                        reply = self.extract_comment(reply, is_reply=True)
                        self.save_comment(reply)
            print(f'Iteration: {iter}, Page count: {page_count}, Total count: {total_count}')
            iter += 1
        return response

    def get_comment_threads(self, channel_id):
        """quote = 10 units per request"""
        request = self.youtube_client.commentThreads().list(
            part="id,snippet,replies",
            allThreadsRelatedToChannelId=channel_id,
            maxResults=100,
            textFormat="plainText",
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
                comment_author,
                comment_author_id,
                comment_author_channel_id,
                comment_published_at,
                comment_updated_at,
                is_reply,
                reply_by_channel_owner
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", comment_tuple)
        conn.commit()
        conn.close()

    def get_closed_captions(self):
        """no longer accessible via data api without authentication by the channel owner"""
        # https://issuetracker.google.com/issues/241669016?pli=1
        pass

    def find_experts(self, topic_list, language='en'):
        """this didn't work very well, but it's a start. Faster to just search browser for convenience sample"""
        def iterate_responses(response):
            for item in response['items']:
                channelID = item['id']['channelId']
                title = item['snippet']['channelTitle']
                description = item['snippet']['description']
                if 'I' in description.split(' '):
                    print(channelID)
                    print(title)
                    print(description)
        
        q = '|'.join(topic_list)

        request = self.youtube_client.search().list(
            part="snippet",
            q=q,
            type='channel',
            #order="viewCount",
            maxResults=50,
            relevanceLanguage=language
        )
        response = request.execute()
        next_page_token = response.get('nextPageToken', None)
        iterate_responses(response)

        count=0
        while next_page_token:
            count+=1
            if count > 15:
                break
            request = self.youtube_client.search().list(
                part="snippet",
                q=q,
                type='channel',
                order="viewCount",
                maxResults=50,
                relevanceLanguage=language,
                pageToken=next_page_token
            )
            response = request.execute()
            next_page_token = response.get('nextPageToken', None)
            iterate_responses(response)


    def extract_comment(self, comment_dict, is_reply=False):
        '''Transform comment dictionary into a tuple'''
        comment_video_id = self.fernet.encrypt(bytes(comment_dict['snippet']['videoId'], 'utf-8')).decode('utf-8')
        comment_channel_id = self.fernet.encrypt(bytes(comment_dict['snippet']['channelId'], 'utf-8')).decode('utf-8')
        comment_id = self.fernet.encrypt(bytes(comment_dict['id'], 'utf-8')).decode('utf-8')
        comment_text = comment_dict['snippet']['textDisplay']
        comment_likes = comment_dict['snippet']['likeCount']
        comment_author = self.fernet.encrypt(bytes(comment_dict['snippet']['authorDisplayName'], 'utf-8')).decode('utf-8')
        comment_author_id = self.fernet.encrypt(bytes(comment_dict['snippet']['authorChannelId']['value'], 'utf-8')).decode('utf-8')
        comment_author_channel_id = self.fernet.encrypt(bytes(comment_dict['snippet']['authorChannelId']['value'], 'utf-8')).decode('utf-8')
        comment_published_at = comment_dict['snippet']['publishedAt']
        comment_updated_at = comment_dict['snippet']['updatedAt']
        reply_by_channel_owner = True if is_reply and comment_channel_id == comment_author_channel_id else False
        return (comment_video_id, comment_channel_id, comment_id, comment_text, comment_likes, comment_author, comment_author_id, comment_author_channel_id, comment_published_at, comment_updated_at, is_reply, reply_by_channel_owner)
        
                
def main():
    extractor = YoutubeExtractor([])
    extractor.get_all_comment_threads("UCVgK5-w1dilMx7bPVB5yNug")
    extractor.get_all_comment_threads("UCSXrEX7LkWOmfTaV6u1C7wQ")


if __name__ == "__main__":
    main()
