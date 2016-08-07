#!/usr/bin/env python

import json
import logging
import os.path
import praw
import sys
import tornado
from praw.errors import OAuthInvalidGrant
from praw.handlers import MultiprocessHandler
from pprint import pprint
from tornado import gen, web, websocket

class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class LinkSocketHandler(websocket.WebSocketHandler):
    links = []

    thread_pool = tornado.concurrent.futures.ThreadPoolExecutor(4)

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    @gen.coroutine
    def open(self):
        self.r = get_reddit_object()
        self.r.set_access_credentials(scope, self.get_secure_cookie("token"))
        message = {
            "message": "init",
            "name": "/u/" + self.r.user.name.encode('utf-8'),
            }
        self.write_message(message)
        yield self.thread_pool.submit(self.get_saved, self.r.get_me())

    def on_message(self, message):
        print message

    def update_link(self, link):
        message = {
            "message": "link",
            "content": tornado.escape.to_basestring(self.render_string('link.html', link=link)),
            }
        self.write_message(message)

    def get_saved(self, user):
        for i in user.get_saved(limit=None, time='all'):
            if i._underscore_names is None: # link posts don't have that attribute, whatever it is
                link = {
                    "self": "False",
                    "url": i.url.encode('utf-8'),
                    "thumbnail": i.thumbnail.encode('utf-8'),
                    "title": i.title.encode('utf-8'),
                    "author": "[deleted]" if not i.author else str(i.author.name),
                    "subreddit": str(i.subreddit.display_name),
                    "permalink": i.permalink.encode('utf-8'),
                    "num_comments": str(i.num_comments),
                }
                self.links.extend([link])
                self.update_link(link)
            else:
                submission = self.r.get_submission(submission_id=i.link_id.encode('utf-8')[3:])
                link = {
                    "self": "True",
                    "link_url": i.link_url.encode('utf-8'),
                    "link_title": i.link_title.encode('utf-8'),
                    "link_author": i.link_author.encode('utf-8'),
                    "subreddit": str(i.subreddit.display_name),
                    "permalink": submission.permalink.encode('utf-8'),
                    "num_comments": str(submission.num_comments),
                    "author": "[deleted]" if not i.author else str(i.author.name),
                    "link_id": i.link_id.encode('utf-8')[3:],
                    "id": i.id.encode('utf-8'),
                    "body": i.body_html.encode('utf-8'),
                }
                self.links.extend([link])
                self.update_link(link)
        message = {
            "message": "done",
            }
        self.write_message(message)

class MainHandler(BaseHandler):
    @web.authenticated
    def get(self):
        try:
            token = self.get_secure_cookie("token")
            if token:
                r.set_access_credentials(scope, token)
            else:
                r.get_access_information(self.get_secure_cookie("user"))
                self.set_secure_cookie("token", r.access_token)

            self.render('index.html', name="/u/" + r.user.name.encode('utf-8'), links=[], js="True")
        except OAuthInvalidGrant:
            self.redirect('/auth')

class AuthHandler(BaseHandler):
    def get(self):
        code = self.get_arguments('code')
        if code:
            self.set_secure_cookie("user", code[0])
            self.redirect("/")
        else:
            url = r.get_authorize_url('reddit-exporter', scope)
            self.render('authenticate.html', link=url)

def read_settings():
    try:
        settings_file = open("reddit-exporter.cfg", "r")
    except IOError:
        logging.exception("Error opening reddit-exporter.cfg.")
        sys.exit(1)

    settings_str = settings_file.read()
    settings_file.close()

    try:
        settings = json.loads(settings_str)
    except ValueError:
        logging.exception("Error parsing settings.json.")
        sys.exit(1)

    if len(settings["client_id"]) == 0:
        logging.critical("ID not set.")
        sys.exit(1)

    if len(settings["client_secret"]) == 0:
        logging.critical("Secret not set.")
        sys.exit(1)

    if len(settings["redirect_uri"]) == 0:
        logging.critical("Redirect URI not set.")
        sys.exit(1)

    return settings

def get_reddit_object():
    r = praw.Reddit('Reddit Saved Links Exporter by /u/ThePaperPilot ver 0.1 see '
                    'https://github.com/thepaperpilot/RedditSavedLinksExporter '
                    'for source',
                    handler=handler)

    r.set_oauth_app_info(client_id=settings['client_id'],
                         client_secret=settings['client_secret'],
                         redirect_uri=settings['redirect_uri'])

    return r

if __name__ == "__main__":
    logging.basicConfig()

    os.system("praw-multiprocess")
    settings = read_settings()
    handler = MultiprocessHandler()
    scope = ['identity', 'history']
    r = get_reddit_object()

    application = web.Application(
        [
            (r"/", MainHandler),
            (r"/auth", AuthHandler),
            (r"/linksocket", LinkSocketHandler),
            ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        login_url="/auth",
        )

    application.listen(65010)
    tornado.ioloop.IOLoop.current().start()

    logging.shutdown()
