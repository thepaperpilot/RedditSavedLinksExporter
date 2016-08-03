#!/usr/bin/env python

import csv
import sys
import logging
import json
import praw

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

    r.login(settings['reddit_username'], settings['reddit_password'], disable_warning=True)

    return r

def getCSV(user):
    csv_fields = ['URL', 'Title', 'Subreddit']
    csv_rows = []
    delimiter = ','

    for i in r.user.get_saved(limit=None, time='all'):
        if not hasattr(i, 'title'):
           i.title = i.link_title
        try:
            subreddit = str(i.subreddit)
        except AttributeError:
            subreddit = "None"
        csv_rows.append([i.permalink.encode('utf-8'), i.title.encode('utf-8'), subreddit])

    with open("export-saved.csv", "w") as f:
        csvwriter = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(csv_fields)
        for row in csv_rows:
            csvwriter.writerow(row)


if __name__ == "__main__":
    logging.basicConfig()

    try:
        settings = readSettings()
        r = getRedditObject()

        getCSV(r.user)

    except:
        logging.exception("Uncaught exception")

    logging.shutdown()
