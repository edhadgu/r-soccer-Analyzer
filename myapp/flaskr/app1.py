import os
from flask import Flask, request, render_template
from rank_bm25 import BM25Okapi
import praw
import spacy

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

    def getBestGoal(timeInterval):
        results = []
        corpus_submissions = []
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            corpus_submissions.append(submission)
        
        tokenized_corpus = [doc.title.split(" ") for doc in corpus_submissions]
        bm25 = BM25Okapi(tokenized_corpus)
        
        query = "goal ' - [ ] 0 1 2 3 4 5" # goal submissions are in the format Team A [score] - score Team B - Player ... minute
        tokenized_query = query.split(" ")
            
        results = bm25.get_top_n(tokenized_query, corpus_submissions, n=10)
        return results

    # Get list of top submissions that have news articles in the given timeInterval
    def getTopnews(timeInterval):
        results = []
        corpus_submissions = []
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            corpus_submissions.append(submission)
        tokenized_corpus_url = [doc.url.replace(".","/").split("/") for doc in corpus_submissions]
        tokenized_corpus = [doc.title.split(" ") for doc in corpus_submissions]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_url = BM25Okapi(tokenized_corpus_url)
        
        query = "FOX ESPN sky twitter athletic"
        tokenized_query = query.split(" ")

        query_url = "twitter news report daily athletic sky fox espn"
        tokenized_query_url = query_url.split(" ")
        
        results = bm25.get_top_n(tokenized_query, corpus_submissions, n=10)
        results_url = bm25_url.get_top_n(tokenized_query_url, corpus_submissions, n=10)  
        combined_results = results + results_url
        results_no_duplicates = []
        [results_no_duplicates.append(x) for x in combined_results if x not in results_no_duplicates]
        return results_no_duplicates

    # Get list of names in the top posts of the given timeInterval
    # This will include teams and player names
    # Teams with two words and full names of players will not be shown due to the tokens being split by a space
    def getFanFavorite(timeInterval):
        nlp = spacy.load("en_core_web_sm")
        corpus_submissions = []
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            corpus_submissions.append(submission)
        
        tokenized_corpus = [nlp(doc.title) for doc in corpus_submissions]

        tokenized_corpus_people = []
        for doc in tokenized_corpus:
            for token in doc.ents:
                if token.label_ == 'PERSON': # check if each individual word is a person
                    tokenized_corpus_people.append(token)
        
        tokenized_corpus_people_clean = []
        # make sure player names only have characters and remove duplicates
        # Sometimes the 
        [tokenized_corpus_people_clean.append(str(people)) for people in tokenized_corpus_people if str(people).isalpha() and str(people) not in tokenized_corpus_people_clean]

        return tokenized_corpus_people_clean
    # Prints out the comments that have the best comment upvote / post upvote ratio
    # Takes very long to loop through comments
    def getBestComments(timeInterval):
        comment_to_score = {}
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=5):
            for comment in (submission.comments)[:2]:
                if "I am a bot" not in str(comment.body): # do not include mod comments
                    comment_to_score[comment] = float(comment.score) / float(submission.score)
        results = dict(sorted(comment_to_score.items(), key=lambda item: item[1], reverse=True))
        return results

    # Tallies up the upvotes each user has in a time period and displays a link to their profile
    def getBestUsers(timeInterval):
        user_to_score = {}
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            user_to_score[str(submission.author)] = float(submission.score)
        
        results = dict(sorted(user_to_score.items(), key=lambda item: item[1], reverse=True))
        return results[:10]

    @app.route('/')
    def index():
        return render_template('index.html', data=['best goals of the', 'fan favorites of the', 'top users of the', 'top news of the', 'best comments of the'], timeInterval=['day', 'week', 'month', 'year', 'all'])
    
    @ app.route("/test", methods=['GET', 'POST'])
    def test():
        topic=request.form.get('topic_select')
        timeInterval=request.form.get('timeInterval_select')
        
        if topic == 'best goals of the':
            return render_template('results.html', data=getBestGoal(timeInterval))
        elif topic == 'top news of the':
            return render_template('results.html', data=getTopnews(timeInterval))
        elif topic == 'fan favorites of the':
            return render_template('results_strings.html', data=getFanFavorite(timeInterval))
        elif topic == 'best comments of the':
            return render_template('results_comments.html', data=getBestComments(timeInterval))
        elif topic == 'top users of the':
            return render_template('results_strings_users.html', data=getBestUsers(timeInterval))
        
        return render_template('results.html', data=getBestGoal(timeInterval))

    return app
