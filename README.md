# r/soccer analyzer
## by Elias Hadgu

An easy way to see the best parts of r/soccer all in one place!

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
    - The app will display the top posts that include a post linking to the video of the goal. Although, due to copyright, videos in older posts will not be viewable
    - This was done by creating a list of corpora (the plural of corpus. I had to look this up lol) where each corpus was the title of a reddit post. Since goals are always in the form `Team [score] - [score] Team - Scorer minute` I made a query that checked for numbers from 0-7 and the `'` and `[]` characters
2. Finding the most popular clubs and people during a given time period
    - This is done by going through the top posts, and identifying the most popular terms that spacy's NLP library views as people, organizations, or locations (this is because many soccer team names are based off of their location).
3. Finding the top users during a given time period
    - The top users are the users with the largest sum of upvotes during the given time period. There is a link to their profile if you want to see what they have posted.
4. Finding the top news articles during a given time period
    - These are found by taking the top posts and querying based on components of the url and the title of the post. Since many articles come from Twitter and news outlets like Sky Sports, ESPN, and the Athletic, these terms are included in both queries
5. Finding the best comments during a given time period
    - The best comments are shown in order of highest comment score / post score ratio. This makes it different from just showing the top comments during a time period as posts with less upvotes would not be shown
    - This will take a while to run
    - There is no profanity checker so beware!
6. Finding the posts with lots of discussion
    - This is found by getting the top 100 posts, sorting them by the ratio between comments and post upvotes, and showing the top 10.
    - This does not include the Match Thread or Daily Discussion posts because they are too obvious. This functionality is geared more towards posts that have good discussion, but not were not solely intended for it.

