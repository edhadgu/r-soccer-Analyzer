import praw

reddit = praw.Reddit("user")
print(reddit.read_only)

for submission in reddit.subreddit("soccer").hot(limit=10):
    print(submission.title)