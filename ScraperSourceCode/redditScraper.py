import os
import praw
from datetime import datetime, timezone
from dotenv import load_dotenv

################################
# Authors:                     #
#   Maxim Subotin - 207695479  #
#   Amiel Cohen - 315196311    #
################################

class RedditScraper:
    def __init__(self, keywords, subreddits):
        # Load .env file
        load_dotenv()

        # Get credentials
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        user_agent = os.getenv('USER_AGENT')

        # Validate credentials
        if not all([client_id, client_secret, user_agent]):
            raise ValueError('Missing Reddit API credentials in the .env file!')

        # Initialize Reddit API client, keywords and subreddits
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.keywords = [word.lower() for word in keywords]
        self.subreddits = subreddits

    def collect_data(self, posts_limit=200, comments_limit=50):
        results = []

        for sub_name in self.subreddits:
            subreddit = self.reddit.subreddit(sub_name)
            found_posts = 0 

            #for post in subreddit.search(' OR '.join(self.keywords), limit=posts_limit * 10):
            for post in subreddit.new(limit=posts_limit * 10):
                if found_posts < posts_limit and any(word in (post.title + ' ' + post.selftext).lower() for word in self.keywords):
                    post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc).strftime('%d-%m-%Y %H:%M:%S')
                    clean_text = post.selftext.replace("\n", " ")
                    post_message = f"{post.title} - {clean_text}"
                    results.append({
                        'ID': post.id,
                        'Username': str(post.author),
                        'Message': post_message,
                        'Likes': post.score,
                        'Timestamp': post_time,
                        'Link': post.url
                    })
                    found_posts += 1 
                    
                    post.comments.replace_more(limit=0)  # Load all comments
                    matched_comments = 0
                    
                    for comment in post.comments.list():
                        if any(word in comment.body.lower() for word in self.keywords):
                            comment_time = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).strftime('%d-%m-%Y %H:%M:%S')
                            results.append({
                                'ID': comment.id,
                                'Username': str(comment.author),
                                'Message': comment.body,
                                'Likes': comment.score,
                                'Timestamp': comment_time,
                                'Link': f'https://www.reddit.com{comment.permalink}'
                            })
                            matched_comments += 1
                        
                        if matched_comments >= comments_limit+1:
                            break
                    
        return results
