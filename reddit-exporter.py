 #!/usr/bin/env python
 # coding=utf-8

import json
import logging
import os.path
import praw
import sys
import tornado
from praw.errors import OAuthInvalidGrant, OAuthInvalidToken
from praw.handlers import MultiprocessHandler
from pprint import pprint, pformat
from tornado import gen, web, websocket

class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class LinkSocketHandler(websocket.WebSocketHandler):
    links = []
    json = '['

    thread_pool = tornado.concurrent.futures.ThreadPoolExecutor(4)

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        pass

    @gen.coroutine
    def on_message(self, msg):
        message = json.loads(msg)
        if message["message"] == "load_oauth":
            self.write_message({"message": "start"})
            self.r = get_reddit_object()
            self.r.set_access_credentials(scope, self.get_secure_cookie("token"))
            self.r.config.store_json_result = True
            yield self.thread_pool.submit(self.get_saved_oauth, self.r.get_me())
        elif message["message"] == "load_json":
            self.write_message({"message": "start"})
            self.r = get_reddit_object()
            self.r.set_access_credentials(scope, self.get_secure_cookie("token"))
            self.r.config.store_json_result = True
            yield self.thread_pool.submit(self.get_saved_json, message["content"])
        elif message["message"] == "json":
            send = {
                "message": "export",
                "content": self.json,
                "name": self.r.user.name.encode('utf-8') + ".json",
                "type": "application/json;charset=utf-8",
            }
            self.write_message(send)
        elif message["message"] == "csv":
            send = {
                "message": "export",
                "content": self.generate_csv(),
                "name": self.r.user.name.encode('utf-8') + ".csv",
                "type": "text/csv;charset=utf-8",
            }
            self.write_message(send)
        elif message["message"] == "md":
            send = {
                "message": "export",
                "content": self.generate_md(),
                "name": self.r.user.name.encode('utf-8') + ".md",
                "type": "text/markdown;charset=utf-8",
            }
            self.write_message(send)
        elif message["message"] == "html":
            send = {
                "message": "export",
                "content": self.generate_html(),
                "name": self.r.user.name.encode('utf-8') + ".html",
                "type": "text/html;charset=utf-8",
            }
            self.write_message(send)

    def update_link(self, link):
        message = {
            "message": "link",
            "content": tornado.escape.to_basestring(self.render_string('link.html', link=link)),
            }
        self.write_message(message)

    def get_saved_oauth(self, user):
        for i in user.get_saved(limit=None, time='all'):
            self.json += json.dumps(i.json_dict, indent=4) + ','
            if isinstance(i, praw.objects.Comment):
                link = {
                    "self": "True",
                    "link_url": i.link_url.encode('utf-8'),
                    "link_title": i.link_title.encode('utf-8'),
                    "link_author": i.link_author.encode('utf-8'),
                    "subreddit": str(i.subreddit.display_name),
                    "permalink": "https://www.reddit.com/r/" + str(i.subreddit.display_name) + "/comments/" + i.link_id.encode('utf-8')[3:],
                    "author": "[deleted]" if not i.author else str(i.author.name),
                    "link_id": i.link_id.encode('utf-8')[3:],
                    "id": i.id.encode('utf-8'),
                    "body": i.body_html.encode('utf-8'),
                }
                self.links.extend([link])
                self.update_link(link)
            else:
                link = {
                    "self": "False",
                    "url": i.url.encode('utf-8'),
                    "thumbnail": i.thumbnail.encode('utf-8'),
                    "title": i.title.encode('utf-8'),
                    "author": "[deleted]" if not i.author else str(i.author.name),
                    "subreddit": str(i.subreddit.display_name),
                    "permalink": i.permalink.encode('utf-8'),
                    "num_comments": str(i.num_comments),
                    "is_self": "True" if (i.is_self) & (i.selftext_html is not None) & (i.selftext != "[removed]") & (i.selftext != "[deleted]") else "False",
                }
                if link["is_self"] == "True":
                    link.update({"body": i.selftext_html})
                self.links.extend([link])
                self.update_link(link)
        self.json = self.json[:-1] + ']'
        self.write_message({"message": "done"})

    def get_saved_json(self, raw):
        self.json = json.dumps(raw, indent=4)
        for submission in raw:
            if "permalink" in submission:
                i = praw.objects.Submission(self.r, submission)
                link = {
                    "self": "False",
                    "url": i.url.encode('utf-8'),
                    "thumbnail": i.thumbnail.encode('utf-8'),
                    "title": i.title.encode('utf-8'),
                    "author": "[deleted]" if not i.author else str(i.author.name),
                    "subreddit": str(i.subreddit.display_name),
                    "permalink": i.permalink.encode('utf-8'),
                    "num_comments": str(i.num_comments),
                    "is_self": "True" if (i.is_self) & (i.selftext_html is not None) & (i.selftext != "[removed]") & (i.selftext != "[deleted]") else "False",
                }
                if link["is_self"] == "True":
                    link.update({"body": i.selftext_html})
                self.links.extend([link])
                self.update_link(link)
            else:
                i = praw.objects.Comment(self.r, submission)
                link = {
                    "self": "True",
                    "link_url": i.link_url.encode('utf-8'),
                    "link_title": i.link_title.encode('utf-8'),
                    "link_author": i.link_author.encode('utf-8'),
                    "subreddit": str(i.subreddit.display_name),
                    "permalink": "https://www.reddit.com/r/" + str(i.subreddit.display_name) + "/comments/" + i.link_id.encode('utf-8')[3:],
                    "author": "[deleted]" if not i.author else str(i.author.name),
                    "link_id": i.link_id.encode('utf-8')[3:],
                    "id": i.id.encode('utf-8'),
                    "body": i.body_html.encode('utf-8'),
                }
                self.links.extend([link])
                self.update_link(link)
        self.write_message({"message": "done"})

    def generate_csv(self):
        csv = 'title,url,author,subreddit,permalink\n'
        for i in self.links:
            csv += (i["link_title"] if i["self"] == "True" else i["title"]).replace(',', '') + ','
            csv += (i["link_url"] if i["self"] == "True" else i["url"]).replace(',', '') + ','
            csv += i["author"].replace(',', '') + ','
            csv += i["subreddit"].replace(',', '') + ','
            csv += ("https://www.reddit.com/comments/" + i["link_id"] + "/" + i["link_title"] + "/" + i["id"] + "/" if i["self"] == "True" else i["permalink"]).replace(',', '') + '\n'
        return csv

    def generate_md(self):
        for i in self.links:
            i['permalink'] = i['permalink'].replace(' ', '%20')
            if i['self'] == "True":
                i['body_md'] = tornado.escape.xhtml_unescape("> " + i['body'].replace('\n', '\n> '))
                i['link_url'] = i['link_url'].replace(' ', '%20')
                i['comment_permalink'] = ("https://www.reddit.com/comments/" + i["link_id"] + "/" + i["link_title"] + "/" + i["id"] + "/").replace(' ', '%20')
            else:
                i['url'] = i['url'].replace(' ', '%20')
        return self.render_string('index.md', name="/u/" + self.r.user.name.encode('utf-8'), links=self.links).replace('﻿', '')

    def generate_html(self):
        return self.render_string('index.html', name="/u/" + self.r.user.name.encode('utf-8'), links=self.links, js="False")

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
        except OAuthInvalidToken:
            self.clear_cookie("token")
            self.redirect('/')

class AuthHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("token")
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

    os.system("praw-multiprocess & disown")
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
