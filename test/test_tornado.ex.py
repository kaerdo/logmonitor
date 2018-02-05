# -*-coding:utf8-*-

from tornado.web import RequestHandler, Application, HTTPError
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import options, define
from uuid import uuid4

class sessionmixin:
    def get_session_id(self):
        session_id = self.request.cookies.get("session_id") 
        return session_id
    
    def set_session_id(self):
        session_id = uuid4().hex 
        self.set_cookie("session_id", session_id)
        return session_id

    def session_get(self, key):
        session_value = self.application.session.get_session(key)
        return session_value

    def session_put(self, session_id, key, value):
        self.application.session.set_session(session_id, key, value)

class IndexHandler(sessionmixin, RequestHandler):
    def get(self):
        if not self.get_session_id():
            session_id = self.set_session_id()
            self.session_put(session_id, "user", "guoning")
        self.write("hello world")

class SessionManage:
    def __init__(self):
        self.session = {} 

    def get_session(self, session_id, key):
        return self.session.get(session_id).get(key)

    def set_session(self, session_id, key, value):
        if session_id not in self.session:
            self.session[session_id] = {key: value}
        else: 
            self.session[session_id][key] = value

    def clean_session(self, session_id):
        self.session.pop(session_id) 

def make_app():
    app = Application(handlers=[(
        '/', IndexHandler
    )], dubug=True)
    setattr(app, "session", SessionManage)
    return app 


if __name__ == '__main__':
    define("port", default=8005, type=int, help="this is port ...")
    options.parse_command_line()
    app = make_app()
    httpserver = HTTPServer(app)
    httpserver.listen(8005)
    IOLoop.instance().start()



