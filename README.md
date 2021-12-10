# r/soccer analyzer
## by Elias Hadgu

An easy way to see the best parts of r/soccer all in one place!

# Getting started

Clone this git repo

Create a reddit app [here](https://www.reddit.com/prefs/apps) so that you can get your `client_id` and `client_secret`

Add a `praw.ini` file under the `flaskr` directory

The syntax should be:
```
[user]
client_id=ENTER_CLIENT_ID_HERE
client_secret=ENTER_CLIENT_SECRET_HERE
user_agent = python:r-soccer-analyzer:v1.0.0 (by Elias Hadgu)
```
You should only edit `client_id` and `client_secret`

The values can be found here after you make your Reddit app:

![](/creds-tutorial.png)

You will not be able to call any PRAW functions without this step

# Running the Application
NOTE: I am using the latest version of Python

cd into the `flaskr` directory and run `py -m flask run` into your desired terminal

If there are no errors, you should be able to click the localhost link and access the app at (http://127.0.0.1:5000/)

# Libraries Used
1. [PRAW](https://praw.readthedocs.io/en/stable/index.html)
     - This is the main API that I used to get access to Reddit posts, comments, and users.
2. [Flask](https://flask.palletsprojects.com/en/2.0.x/)
     - Main UI of the app
4. [rank_bm25](https://pypi.org/project/rank-bm25/)
     - Used for BM25Okapi queries when getting top goals and news reports
6. [spacy](https://spacy.io/usage)
     - Used for token tagging when figuring out if a token is a player or team name

rank_bm25 and spacy must be downloaded according to the links provided in order for the app to work

# Uses

the r/soccer analyzer is a tool used for getting information from the r/soccer subreddit that is not easily done through the Reddit search feature. The current features are:

1. Finding the best goal during a given time period
    - The app will display the top posts that include a post linking to the video of the goal. Although, due to copyright, videos in older posts will not be viewable
2. Finding the most popular clubs and people during a given time period
    - This is done by going through the top posts, and identifying the most popular terms that spacy's NLP library views as people. Since each token is only one word, some teams are listed as people and are counted
3. Finding the top users during a given time period
    - The top users are the users with the largest sum of upvotes during the given time period
4. Finding the top news articles during a given time period
    - These are found by taking the top posts and querying based on components of the url and the title of the post. Since many articles come from Twitter and news outlets like Sky Sports, ESPN, and the Athletic, these terms are included in both queries
5. Finding the best comments during a given time period
    - The best comments are shown in order of highest comment score / post score ratio. This makes it different from just showing the top comments during a time period as posts with less upvotes would not be shown

