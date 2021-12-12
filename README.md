# r/soccer analyzer (Documentation is in this README)
## by Elias Hadgu

An easy way to see the best parts of r/soccer all in one place!

# Presentation

https://drive.google.com/file/d/1v5ShiY6XSafM-a8gsoZXDIyyk4ckNUVW/view?usp=sharing

# Getting started

Clone this git repo

download [Flask](https://flask.palletsprojects.com/en/2.0.x/installation/)
```
pip install flask
```
Set the `FLASK_APP` environment variable (make sure you are in the `flaskr` directory)
```
export FLASK_APP=app1
```
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

Next, you need to install the libraries used: [rankbm25](https://pypi.org/project/rank-bm25/) and [spacy](https://spacy.io/usage):

```
pip install rank_bm25

pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
```

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
    ```
    bm25 = BM25Okapi(tokenized_corpus)
        
    query = "goal ' - [ ] [0] [1] [2] [3] [4] [5] [6] [7]"
    
    tokenized_query = query.split(" ")

    # gets the top 10 Reddit posts that have the highest ranking according to BM25Okapi     
    results = bm25.get_top_n(tokenized_query, corpus_submissions, n=10)
    ```
     
6. [spacy](https://spacy.io/usage)
     - Used for token tagging when figuring out if a token is a player or team name
     ```
    tokenized_corpus_people_or_team = []
    for doc in tokenized_corpus:
        for token in doc.ents:
            if token.label_ == 'PERSON' or token.label_ == 'GPE':
                tokenized_corpus_people_or_team.append(token)
     ```

rank_bm25 and spacy must be downloaded according to the links provided in order for the app to work

# Uses

the r/soccer analyzer is a tool used for getting information from the r/soccer subreddit that is not easily done through the Reddit search feature. The current features are:

1. Finding the best goal during a given time period
    - This is a great way to easily watch the best goals without directly searching for a specific goal and since each link takes you directly to a video link, it takes less effort that actually going on Reddit
    - The app will display the top posts that include a post linking to the video of the goal. Although, due to copyright, videos in older posts will not be viewable
    - This was done by creating a list of corpora (the plural of corpus. I had to look this up lol) where each corpus was the title of a reddit post. Since goals are always in the form `Team [score] - [score] Team - Scorer minute'` I made a query that checked for numbers from 0-7 enclosed in brackets and the `'` character
2. Finding the most popular clubs and people during a given time period
    - This option is great if you want to figure out the hot topics in the subreddit during a given time period. One feature I would add if I had more time would be a plot for each topic showing its popularity over time graph
    - This is done by going through the top posts, and identifying the most popular terms that spacy's NLP library views as people, organizations, or locations (this is because many soccer team names are based off of their location)
    - I tried to implement stemming so that phrases such as 'Lionel Messi' and 'Messi' would count as the same thing, but I could not implement it the way I wanted to. I also had to add some extra conditionals as some terms marked as people or teams had special characters and didn't make sense
3. Finding the top users during a given time period
    - Since the r/soccer subreddit does not have any rewards for its users, this tool is a good way to keep track of the top contributors of the subreddit
    - The top users are the users with the largest sum of upvotes during the given time period. There is a link to their profile if you want to see what they have posted. There is no profanity checker on usernames so beware!
4. Finding the top news articles during a given time period
    - If you just want to see soccer news without the many other posts in the subreddit, you can use this option
    - Top news articles are found by taking the top posts and querying based on components of the url and the title of the post. Since many articles come from Twitter and news outlets like Sky Sports, ESPN, and the Athletic, these terms are included in both queries
    - Sometimes, goal videos were coming up as articles so I added extra conditionals so that if 'stream' or 'gg', which are common in video links, were in the url, it would not be counted as an article
5. Finding the best comments during a given time period
    - Sometimes, the comments of a post can be better than the post itself. This tool highlights comments that have high upvotes relative to the upvotes of the post it's responding to
    - The best comments are shown in order of highest comment score / post score ratio. This makes it different from just showing the top comments during a time period as posts with less upvotes would not be shown
    - This will take a while to run. I tried to only loop through the top 5 posts and top 2 comments in each post but looping through comments in PRAW takes a very long time
    - There is no profanity checker for comments so beware!
6. Finding the posts with lots of discussion
    - Although Reddit has its own filter for contraversial, that is based more on upvotes and downvotes. This option allows the user to look at posts that have promoted discussion among users
    - This is found by getting the top 100 posts, sorting them by the ratio between comments and post upvotes, and showing the top 10
    - This does not include the Match Thread or Daily Discussion posts because they are too obvious. This functionality is geared more towards posts that have good discussion, but not were not solely intended for it
    - An issue I stumbled upon while working on this feature was that if a Reddit post contains a link (such as a video or twitter link), it is impossible to get the link of the actual post using PRAW. Because of this, if a post contains a link, you will not be able to access the Reddit post and see the comments through this app

# Note

This was my first experience with front end development and learning Flask, HTML, and CSS took up a decent chunk of my development time.

