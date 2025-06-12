import os
import asyncio
from TikTokApi import TikTokApi # https://github.com/davidteather/TikTok-Api

################################
# Authors:                     #
#   Maxim Subotin - 207695479  #
#   Amiel Cohen - 315196311    #
################################

class TikTokScraper:
    def __init__(self, ms_token=None, browser="chromium"):
        self.ms_token = ms_token or os.environ.get("ms_token", None)
        self.browser = browser

    async def collect_data(self, video_count=3, comments_per_video=5):
        results = []
        async with TikTokApi() as api:
            await api.create_sessions(
                headless=False,
                ms_tokens=[self.ms_token],
                num_sessions=1,
                sleep_after=3,
                browser=self.browser
            )
            
            # Fetch trending video IDs
            list_of_video_ids = []
            async for video in api.trending.videos(count=video_count):
                list_of_video_ids.append(video.id)

            # Fetch comments from each video
            for video_id in list_of_video_ids:
                video = api.video(id=video_id)
                async for comment in video.comments(count=comments_per_video):
                    try:
                        results.append({
                            'ID': comment.id,
                            'Username': comment.author.username,
                            'Message': comment.text,
                            'Likes': comment.likes_count,
                            'Timestamp': 'N\A', #this API does not provide a way to get comment timestamps
                            'Link': f'https://www.tiktok.com/@{comment.author.username}/video/{video_id}'
                        })
                    except Exception as e:
                        print(f'Error fetching comment data: {e}')
        
        return results

# # Example usage
# if __name__ == "__main__":
#     scraper = TikTokScraper()
#     comments = asyncio.run(scraper.collect_data())
#     print(comments)