import os
from flask import Flask, request, render_template
from rank_bm25 import BM25Okapi
import praw
import spacy

reddit = praw.Reddit("user")

def contains_number_or_special(s):
    special_characters = '"!@#$%^&*()-+?_=,<>/"'
    for char in s:
        if char.isdigit() or char in special_characters or char == "'":
            return True
    return False
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
        
        # goal submissions are in the format Team A [score] - score Team B - Player ... minute
        query = "goal ' - [0] [1] [2] [3] [4] [5] [6] [7]" 
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
        
        query = "FOX ESPN sky twitter athletic official"
        tokenized_query = query.split(" ")

        query_url = "twitter news report daily athletic sky fox espn"
        tokenized_query_url = query_url.split(" ")
        
        results = bm25.get_top_n(tokenized_query, corpus_submissions, n=10)
        results_url = bm25_url.get_top_n(tokenized_query_url, corpus_submissions, n=10)  
        combined_results = results + results_url
        results_no_duplicates = []
        [results_no_duplicates.append(x) for x in combined_results if x not in results_no_duplicates and " - " not in x.title and "stream" not in x.url and "gg" not in x.url and  "clip" not in x.url and  "v.reddit" not in x.url]
        return list(results_no_duplicates)[:10]

    # Get list of names in the top posts of the given timeInterval
    # This will include teams and player names
    def getFanFavorite(timeInterval):
        nlp = spacy.load("en_core_web_sm")
        corpus_submissions = []
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            corpus_submissions.append(submission)
        
        tokenized_corpus = [nlp(doc.title) for doc in corpus_submissions]

        tokenized_corpus_people_or_team = []
        for doc in tokenized_corpus:
            for token in doc.ents:
                if token.label_ == 'PERSON' or token.label_ == 'GPE': # check if each individual word is a person or team
                    tokenized_corpus_people_or_team.append(token)
        
        tokenized_corpus_people_clean = []
        # make sure player names only have characters and remove duplicates
        # Sometimes the 
        [tokenized_corpus_people_clean.append(str(people)) for people in tokenized_corpus_people_or_team if not contains_number_or_special(str(people)) and str(people) not in tokenized_corpus_people_clean]

        return tokenized_corpus_people_clean[:10]
    
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
        return list(results)[:10]
    # Gets the posts with the highest comment/upvote ratio
    # Does not include the Match Threads or Discussion posts as those are obvious. 
    # This function is to find good discussions where the point of the post was not originally discussion
    def getBestDiscussion(timeInterval):
        submission_to_score = {}
        for submission in reddit.subreddit("soccer").top(time_filter=str(timeInterval), limit=100):
            submission_to_score[submission] = float(submission.num_comments) / float(submission.score)
        
        results = dict(sorted(submission_to_score.items(), key=lambda item: item[1], reverse=True))
        results_without_match_thread = []
        [results_without_match_thread.append(x) for x in results if "Match Thread" not in x.title and "Discussion" not in x.title]
        return list(results_without_match_thread)[:10]

    @app.route('/')
    def index():
        return render_template('index.html', data=['Best Goals of the', 'Most Popular Topics of the', 'Top Users of the', 'Top Articles of the', 'Best Comments of the', 'Best Discussions of the'], timeInterval=['Day', 'Week', 'Month', 'Year', 'All'])
    
    @ app.route("/test", methods=['GET', 'POST'])
    def test():
        topic=request.form.get('topic_select')
        timeInterval=request.form.get('timeInterval_select')
        
        if topic == 'Best Goals of the':
            return render_template('results.html', data=getBestGoal(timeInterval.lower()))
        elif topic == 'Top Articles of the':
            return render_template('results.html', data=getTopnews(timeInterval.lower()))
        elif topic == 'Most Popular Topics of the':
            return render_template('results_strings.html', data=getFanFavorite(timeInterval.lower()))
        elif topic == 'Best Comments of the':
            return render_template('results_comments.html', data=getBestComments(timeInterval.lower()))
        elif topic == 'Top Users of the':
            return render_template('results_strings_users.html', data=getBestUsers(timeInterval.lower()))
        elif topic == 'Best Discussions of the':
            return render_template('results.html', data=getBestDiscussion(timeInterval.lower()))
        
        return render_template('results.html', data=getBestGoal(timeInterval.lower()))

    return app
