# -*-coding:utf8-*-

from tornado.web import Application
from kazoo.client import KazooClient
from tornado.options import options, define

define("port", default=8005, type=int, help="Port")
define("bind", default="0.0.0.0", type=str, help="Host or bind_IP")
define("zkconnect", default="127.0.0.1:2181", type=str, help="zookeeper connect info")
define("zkroot", default="/logmonitor", type=str, help="zk root directory")


def make_app(router, **settings):
    app = Application(router, **settings)
    zk = KazooClient(hosts=options.zkconnect)
    setattr(app, 'zk', zk)
    setattr(app, 'options', options)
    return app
