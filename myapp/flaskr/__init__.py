import os

from flask import Flask, request, render_template
import praw

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

    
    def getResponse(topic, timeInterval):
        result = ''
        for submission in reddit.subreddit("soccer").search("goal", time_filter=str(timeInterval), limit=1): #change to be based on input (not just goal)
            #timeInterval doesn't change anything
            result += submission.title + '\n'
        return str(result)

    @app.route('/')
    def index():
        return render_template('index.html', data=[{'topic': 'best goal of the'}, {'topic': 'fan favorite of the'}, {'topic': 'best player of the'}, {'topic': 'most popular team of the'}, {'topic': 'top user of the'}, {'topic': 'clip of the'}, {'topic': 'top source of the'}], timeInterval=[{'timeInterval': 'day'}, {'timeInterval': 'week'}, {'timeInterval': 'month'}, {'timeInterval': 'year'}, {'timeInterval': 'all'}])
    @ app.route("/test", methods=['GET', 'POST'])
    def test():
        topic=request.form.get('topic_select')
        timeInterval=request.form.get('timeInterval_select')
        print(timeInterval)
        return(getResponse(topic,timeInterval))

    return app
