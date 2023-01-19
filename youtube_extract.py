'''
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

load_dotenv()

class YoutubeExtractor:
    def __init__(self, topic_list, languages=['en']):
        self.topic_list = topic_list
        self.languages = languages
        api_service_name = "youtube"
        api_version = "v3"
        self.youtube_client = googleapiclient.discovery.build(
            api_service_name,
            api_version, 
            developerKey = os.getenv('YOUTUBE_API_KEY')
        )

    def get_video_stats(self):
        dementia_vid = 'q3NgWY-BAJw'
        request = self.youtube_client.videos().list(
            part="contentDetails,topicDetails,snippet,statistics",
            id=dementia_vid
        )
        response = request.execute()
        print(response)

    def get_comment_threads(self):
        request = self.youtube_client.commentThreads().list(
            part="id,snippet,replies",
            allThreadsRelatedToChannelId="UCVgK5-w1dilMx7bPVB5yNug",
            textFormat="plainText"
        )
        response = request.execute()
        print(response)

        # request = self.youtube_client.comments().list(
        #     part="snippet",
        #     maxResults=100,
        #     parentId="UgzDE2tasfmrYLyNkGt4AaABAg"
        # )

    def get_closed_captions(self):
        '''no longer accessible via data api without authentication by the channel owner'''
        # https://issuetracker.google.com/issues/241669016?pli=1
        pass

    def find_experts(self, topic_list, language='en'):
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
            # order="viewCount",
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
                # order="viewCount",
                maxResults=50,
                relevanceLanguage=language,
                pageToken=next_page_token
            )
            response = request.execute()
            next_page_token = response.get('nextPageToken', None)
            iterate_responses(response)

        



        #print(response)
        
                
def main():
    expert_finder = YoutubeExtractor([])
    expert_finder.find_experts(['dementia|alzheimer'])

if __name__ == "__main__":
    main()
