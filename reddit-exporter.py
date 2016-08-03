#!/usr/bin/env python

from flask import Flask, request
import sys
import logging
import json
import praw
import webbrowser

app = Flask(__name__)

URI = 'http://127.0.0.1:65010/'

def readSettings():
    try:
        settingsFile = open("reddit-exporter.cfg", "r")
    except IOError:
        logging.exception("Error opening reddit-exporter.cfg.")
        sys.exit(1)

    settingStr = settingsFile.read()
    settingsFile.close()

    try:
        settings = json.loads(settingStr)
    except ValueError:
        logging.exception("Error parsing settings.json.")
        sys.exit(1)

    if (len(settings["client_id"]) == 0):
        logging.critical("ID not set.")
        sys.exit(1)

    if (len(settings["client_secret"]) == 0):
        logging.critical("Secret not set.")
        sys.exit(1)

    return settings

def getRedditObject():
    r = praw.Reddit('Reddit Saved Links Exporter by /u/ThePaperPilot ver 0.1 see '
                    'https://github.com/thepaperpilot/RedditSavedLinksExporter '
                    'for source')

    r.set_oauth_app_info(client_id=settings['client_id'],
                         client_secret=settings['client_secret'],
                         redirect_uri=URI + 'authorize_callback')

    return r

def getCSV(user):
    # csv setting
    csv_rows = []

    csv_rows.append("<tr><th>Post</th><th>Subreddit</th></tr>")

    # filter saved item for link
    for i in user.get_saved(limit=None, time='all'):
        if not hasattr(i, 'title'):
           i.title = i.link_title
        try:
            subreddit = str(i.subreddit)
        except AttributeError:
            subreddit = "None"
        csv_rows.append("<tr><th><a href=" + i.permalink.encode('utf-8') + ">" + i.title.encode('utf-8') + "</a></th><th>" + subreddit + "</th></tr>")

    return '<table style="width=100%">' + "</br>".join(csv_rows) + "<\table>"

@app.route('/')
def homepage():
    url = r.get_authorize_url('reddit-exporter', ['identity', 'read'])
    link = "<a href=%s>link</a>" % url
    text = "Authenticate. %s</br></br>" % link
    return text

@app.route('/authorize_callback')
def authorized():
    code = request.args.get('code', '')
    r.get_access_information(code)
    user = r.get_me()

    text = getCSV(user)

    return text

if __name__ == "__main__":
    logging.basicConfig()

    try:
        settings = readSettings()
        r = getRedditObject()

        webbrowser.open(URI)
        app.run(debug=True, port=65010)
    except:
        logging.exception("Uncaught exception")

    logging.shutdown()
