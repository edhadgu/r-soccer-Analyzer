import os

from flask import Flask, request, render_template
from rank_bm25 import BM25Okapi
import praw
import numpy as np

reddit = praw.Reddit("user")

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def getbestGoal(timeInterval):
        results = []
        corpus_submissions = []
        #for submission in reddit.subreddit("soccer").search("goal", time_filter=str(timeInterval), limit=5): #change to be based on input (not just goal)
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            corpus_submissions.append(submission)
        
        tokenized_corpus = [doc.title.split(" ") for doc in corpus_submissions]
        bm25 = BM25Okapi(tokenized_corpus)
        
        query = "goal ' - [ ] 0 1 2 3 4 5" # goal submissions are in the format Team A [score] - score Team B - Player ... minute
        tokenized_query = query.split(" ")
            
        results = bm25.get_top_n(tokenized_query, corpus_submissions, n=10)
        return results

    def getMostPopularTeam(timeInterval):
        results = []
        corpus = []
        #for submission in reddit.subreddit("soccer").search("goal", time_filter=str(timeInterval), limit=5): #change to be based on input (not just goal)
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            corpus.append(submission.title)
        
        tokenized_corpus = [doc.split(" ") for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        
        query = "club team" # goal submissions are in the format Team A [score] - score Team B - Player ... minute
        tokenized_query = query.split(" ")
            
        results = bm25.get_top_n(tokenized_query, corpus, n=10)
        return results

    @app.route('/')
    def index():
        return render_template('index.html', data=['best goal of the', 'fan favorite of the', 'best player of the', 'most popular team of the', 'top user of the', 'clip of the', 'top source of the'], timeInterval=['day', 'week', 'month', 'year', 'all'])
    
    @ app.route("/test", methods=['GET', 'POST'])
    def test():
        topic=request.form.get('topic_select')
        timeInterval=request.form.get('timeInterval_select')
        
        if topic == 'best goal of the':
            return render_template('results.html', data=getbestGoal(timeInterval))
        elif topic == 'most popular team of the':
            return render_template('results.html', data=getMostPopularTeam(timeInterval))
        return render_template('results.html', data=getbestGoal(timeInterval))

    return app
