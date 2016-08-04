#!/usr/bin/env python

from flask import Flask, request
from pprint import pprint
import sys
import logging
import json
import praw

app = Flask(__name__)

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
                         redirect_uri=settings['redirect_uri'])

    return r

def getCSV(user):
    csv = ''
    md = ''
    html = '<div style="text-align: center;font-size: large;padding-top: 60px;">\n<a href="https://www.reddit.com/user/' + user.name.encode('utf-8') + '">/u/' + user.name.encode('utf-8') + '</a>\n</div>\n<div class="container">\n'

    # TODO Send up a static webpage with a loading icon but not the content (at first), and use javascript to iterate over this and add the posts to a div as they become ready, and remove the loader at the end
    for i in user.get_saved(): # (limit=None, time='all'): # This takes a REALLY long time
        # pprint(vars(i))
        if not hasattr(i, 'title'):
           i.title = i.link_title
        # TODO CSV, MD, and HTML
        if (i._underscore_names == None):
            html += '<div class="link">\n<a href="' + i.url.encode('utf-8') + '" class="thumbnail"><img class="pic" src="' + ('https://b.thumbs.redditmedia.com/ueGKKytgsoCNMne-N18pP8-_fBAMELl02YrlMrlYG2Y.png' if (i.thumbnail == None) | (i.thumbnail == 'self') | (i.thumbnail == 'default') | (i.thumbnail == '') else i.thumbnail.encode('utf-8')) + '"/></a>\n'
            html += '<div style="display: inline;">\n<p class="title">\n<a href="' + i.url.encode('utf-8') + '">' + i.title.encode('utf-8') + '</a>\n</p>\n'
            html += '<p class="tagline">\nsubmitted by <a class="reddit" href="https://www.reddit.com/user/' + str(i.author.name) + '">' + str(i.author.name) + '</a> to <a class="reddit" href="https://www.reddit.com/r/' + str(i.subreddit.display_name) + '">' + str(i.subreddit.display_name) + '</a> with <a class="reddit" href="' + i.permalink.encode('utf-8') + '">' + str(i.num_comments) + ' comments</a>\n</p>\n' + '</div>\n</div>\n'
        else:
            submission = r.get_submission(submission_id=i.link_id.encode('utf-8')[3:])
            html += '<div class="link">\n<p class="tagline" style="margin-top: 16px;">\n<a href="' + i.link_url.encode('utf-8') + '">' + i.link_title.encode('utf-8') + '</a> by <a class="reddit" href="https://www.reddit.com/user/' + i.link_author.encode('utf-8') + '">' + i.link_author.encode('utf-8') + '</a> in <a class="reddit" href="https://www.reddit.com/r/' + str(i.subreddit.display_name) + '">' + str(i.subreddit.display_name) + '</a> with <a class="reddit" href="' + submission.permalink.encode('utf-8') + '">' + str(submission.num_comments) + ' comments</a>\n</p>\n'
            html += '<p class="tagline">\n<a class="reddit" href="https://www.reddit.com/user/' + str(i.author.name) + '">' + str(i.author.name) + '</a>\t<a href="https://www.reddit.com/comments/' + i.link_id.encode('utf-8')[3:] + '/' + submission.title.encode('utf-8').replace(' ', '_') + '/' + i.id.encode('utf-8') + '/">permalink</a>\n</p>\n'
            html += '<div class="link" style="margin: 4px;">\n' + i.body_html.encode('utf-8') + '\n</div>\n</div>\n'

    html += '</div>'

    return html #'<table style="width=100%">' + "".join(csv_rows) + "</table>"

@app.route('/')
def homepage():
    url = r.get_authorize_url('reddit-exporter', ['identity', 'read', 'history'])
    content = '<a class="button" href=%s>\nAuthenticate\n</a>' % url
    with open('authenticate.html') as html:
        return html.read().replace('{{ content }}', content)

@app.route('/authorize_callback')
def authorized():
    code = request.args.get('code', '')
    try :
        r.get_access_information(code)
    except:
        return homepage()
    user = r.get_me()

    content = getCSV(user)

    with open('index.html') as html:
        with open('navbar.html') as navbar:
            return html.read().replace('{{ content }}', content + navbar.read())

if __name__ == "__main__":
    logging.basicConfig()

    try:
        settings = readSettings()
        r = getRedditObject()

        app.run(debug=True, port=65010)
    except:
        logging.exception("Uncaught exception")

    logging.shutdown()
