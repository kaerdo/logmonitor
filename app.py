# -*-coding:utf8-*-

from tornado.ioloop import IOLoop
from tornado.options import options, define
from monitor_api import make_app
from monitor_api.loghandler import FileHandler, RuleHandler


if __name__ == '__main__':
    options.parse_command_line()
    options.parse_config_file("app_config")
    router = [
        ('/file', FileHandler),
        ('/rule', RuleHandler)
        ]
    app = make_app(router, debug=True)
    app.listen(options.port, address=options.bind)
    try:
        app.zk.start()
        IOLoop.current().start()
    except KeyboardInterrupt:
        app.zk.stop()
        IOLoop.current().stop()
