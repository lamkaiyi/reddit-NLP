import os
from dotenv import load_dotenv
import praw
import time
import json
import praw.models
from tqdm import tqdm
import argparse
import datetime

# Load the .env file
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


def create_parser():
    """
    Defines an argument parser for command-line arguments.

    Returns:
        argparse.ArgumentParser: Configured parser object.
    """
    parser = argparse.ArgumentParser(description="GeoTIFF file creation using rasterio.")

    # Define arguments
    parser.add_argument("--subreddit_name", type=str, required=True, help="Name of subreddit to scrape.")
    parser.add_argument("--comments", type=int, required=False, default=0, help='Scrape comments in the post')
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--year", type=int)
    return parser



parser = create_parser()
args = parser.parse_args()

reddit = praw.Reddit(
    user_agent=True,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=USERNAME,
    password=PASSWORD
)



subreddit_name = args.subreddit_name
subreddit = reddit.subreddit(subreddit_name)

# Define the target year (e.g. 2024)
START_DATE = f"{args.year}-01-01"
END_DATE = f"{args.year + 1}-01-01"

# Convert target date to timestamp range
start_datetime = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
end_datetime = datetime.datetime.strptime(END_DATE, "%Y-%m-%d")
start_timestamp = int(start_datetime.timestamp())  
end_timestamp = int(end_datetime.timestamp())  

print(f"scraping year {args.year}")

all_posts = []
with tqdm() as pbar:
    for i, post in enumerate(subreddit.top(limit=None)):  
    
        if start_timestamp <= post.created_utc < end_timestamp:

            return_obj = {
                'title': post.title,
                'text': post.selftext,
                "date": datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "title": post.title,
                "score": post.score,
                "url": post.url,
                "num_comments": post.num_comments,
            }
            
            if args.comments > 0:
                # post.comments.replace_more(limit=None) # expand nested comments
                all_comments = [] # add each comment to list

                for comment in post.comments.list():
                    if isinstance(comment, praw.models.MoreComments):
                        continue # skip nested comments
                    
                    if comment.distinguished == "moderator":
                        continue  # Skip moderator actions such as reminders and rules

                    all_comments.append(comment.body) # add parent comment
                return_obj['comments'] = all_comments
                
            all_posts.append(return_obj)
            pbar.update(1)
            time.sleep(1)

print(f"Collected {len(all_posts)} posts")

# Writing list of dictionaries to a JSON file
with open(args.output_file, "w", encoding="utf-8") as f:
    json.dump(all_posts, f, indent=4)  # `indent=4` makes it readable





