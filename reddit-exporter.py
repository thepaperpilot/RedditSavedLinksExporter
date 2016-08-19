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
        self.r = get_reddit_object()
        self.r.set_access_credentials(scope, self.get_secure_cookie("token"))
        self.r.config.store_json_result = True

    @gen.coroutine
    def on_message(self, msg):
        message = json.loads(msg)
        if message["message"] == "load_oauth":
            self.write_message({"message": "start"})
            yield self.thread_pool.submit(self.get_saved_oauth, self.r.get_me())
        elif message["message"] == "load_json":
            self.write_message({"message": "start"})
            yield self.thread_pool.submit(self.get_saved_json, message["content"])
        elif message["message"] == "json":
            self.export(self.json, "json", "application/json;charset=utf-8")
        elif message["message"] == "csv":
            self.export(self.generate_csv(), "csv", "text/csv;charset=utf-8")
        elif message["message"] == "md":
            self.export(self.generate_md(), "md", "text/markdown;charset=utf-8")
        elif message["message"] == "html":
            self.export(self.generate_html(), "html", "text/html;charset=utf-8")
        elif message["message"] == "delete":
            self.thread_pool.submit(self.delete_links)

    def export(self, content, extension, media):
        self.write_message({
            "message": "export",
            "content": content,
            "name": self.r.user.name.encode('utf-8') + "." + extension,
            "type": media,
            })

    def update_link(self, link):
        self.write_message(message = {
            "message": "link",
            "content": tornado.escape.to_basestring(self.render_string('link.html', link=link)),
            })

    def get_saved_oauth(self, user):
        for i in user.get_saved(limit=None, time='all'):
            self.json += json.dumps(i.json_dict, indent=4) + ','
            if isinstance(i, praw.objects.Comment):
                self.readComment(i)
            else:
                self.readSubmission(i)
        self.json = self.json[:-1] + ']'
        self.write_message({"message": "done"})

    def get_saved_json(self, raw):
        self.json = json.dumps(raw, indent=4)
        for submission in raw:
            if "permalink" in submission:
                self.readSubmission(praw.objects.Submission(self.r, submission))
            else:
                self.readComment(praw.objects.Comment(self.r, submission))
        self.write_message({"message": "done"})

    def readComment(self, comment):
        link = {
            "self": "True",
            "link_url": comment.link_url.encode('utf-8'),
            "link_title": comment.link_title.encode('utf-8'),
            "link_author": comment.link_author.encode('utf-8'),
            "subreddit": str(comment.subreddit.display_name),
            "permalink": "https://www.reddit.com/r/" + str(comment.subreddit.display_name) + "/comments/" + comment.link_id.encode('utf-8')[3:],
            "author": "[deleted]" if not comment.author else str(comment.author.name),
            "link_id": comment.link_id.encode('utf-8')[3:],
            "id": comment.id.encode('utf-8'),
            "body": comment.body_html.encode('utf-8'),
        }
        self.links.extend([link])
        self.update_link(link)

    def readSubmission(self, submission):
        link = {
            "self": "False",
            "url": submission.url.encode('utf-8'),
            "thumbnail": submission.thumbnail.encode('utf-8'),
            "title": submission.title.encode('utf-8'),
            "author": "[deleted]" if not submission.author else str(submission.author.name),
            "subreddit": str(submission.subreddit.display_name),
            "permalink": submission.permalink.encode('utf-8'),
            "num_comments": str(submission.num_comments),
            "id": submission.id.encode('utf-8'),
            "is_self": "True" if (submission.is_self) & (submission.selftext_html is not None) & (submission.selftext != "[removed]") & (submission.selftext != "[deleted]") else "False",
        }
        if link["is_self"] == "True":
            link.update({"body": submission.selftext_html})
        self.links.extend([link])
        self.update_link(link)

    def delete_links(self):
        links = json.loads(self.json)
        for i in links:
            if "permalink" in i:
                link = praw.objects.Submission(self.r, i)
            else:
                link = praw.objects.Comment(self.r, i)
            message = {
                "message": "remove",
                "content": link.id.encode('utf-8'),
            }
            link.unsave()
            self.write_message(message)

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
                access_information = r.get_access_information(self.get_secure_cookie("user"))
                self.set_secure_cookie("token", access_information["access_token"])
                self.set_secure_cookie("refresh", access_information["refresh_token"])

            self.render('index.html', name="/u/" + r.user.name.encode('utf-8'), links=[], js="True")
        except OAuthInvalidGrant:
            self.redirect('/auth')
        except OAuthInvalidToken:
            refresh = self.get_secure_cookie("refresh")
            if refresh:
                try:
                    self.set_secure_cookie("token", r.refresh_access_information(refresh)["access_token"])
                except:
                    self.clear_cookie("refresh")
                    self.clear_cookie("token")
            else:
                self.clear_cookie("token")
            self.redirect('/')

class AuthHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("token")
        self.clear_cookie("refresh")
        code = self.get_arguments('code')
        if code:
            self.set_secure_cookie("user", code[0])
            self.redirect("/")
        else:
            url = r.get_authorize_url('reddit-exporter', scope, refreshable=True)
            self.render('authenticate.html', link=url)

def read_settings():
    try:
        settings_file = open("reddit-exporter.cfg", "r")
    except IOError:
        logging.exception("Error opening reddit-exporter.cfg.")
        sys.exit(1)

    settings_str = settings_file.read()
    settings_file.close()

    return json.loads(settings_str)

def get_reddit_object():
    reddit = praw.Reddit('Reddit Saved Links Exporter by /u/ThePaperPilot ver 0.1 see '
                    'https://github.com/thepaperpilot/RedditSavedLinksExporter '
                    'for source',
                    handler=handler)

    reddit.set_oauth_app_info(client_id=settings['client_id'],
                         client_secret=settings['client_secret'],
                         redirect_uri=settings['redirect_uri'])

    return reddit

logging.basicConfig()

os.system("praw-multiprocess & disown")
settings = read_settings()
handler = MultiprocessHandler()
scope = ['identity', 'history', 'save']
r = get_reddit_object()

application = web.Application(
    [
        (r"/", MainHandler),
        (r"/auth", AuthHandler),
        (r"/linksocket", LinkSocketHandler),
        ],
    cookie_secret=settings['cookie_secret'],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    login_url="/auth",
    )

application.listen(65010)
tornado.ioloop.IOLoop.current().start()

logging.shutdown()
