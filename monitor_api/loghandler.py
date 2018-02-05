#!/usr/bin/env python
# -*-coding:utf8-*-

from tornado.web import RequestHandler, HTTPError
import json
from os import path
from base64 import urlsafe_b64encode

class RestfulMixin:
    def jsonify(self, **karge):
        self.set_header('content-type', 'application/json')
        self.write(json.dumps(karge))

    def payload(self):
        try:
            return json.loads(self.request.body)
        except Exception as e:
            raise HTTPError(400, log_message=str(e))

    def _handle_request_exception(self, e):
        if isinstance(e, HTTPError):
            self.set_status(e.status_code, reason=e.reason)
            self.jsonify(code=e.status_code, message=e.reason)
            self.finish()
            return
        self.set_status(500, reason=str(e))
        self.jsonify(code=e.status_code, message=str(e), exception=e.__class__)


class FileHandler(RestfulMixin, RequestHandler):

    def delete(self, *args, **kargs):
        uargs = self.payload()
        filename = urlsafe_b64encode(uargs.get("filename"))
        files = self.application.zk.get_children(path.abspath(self.application.options.zkroot))
        node = path.abspath(path.join(self.application.options.zkroot, \
                   filename))
        if filename in files:
            try:
                self.application.zk.delete(node.decode(), recursive=True)
            except HTTPError as e:
                raise HTTPError(500, log_message=str(e), reason=str(e))
            self.jsonify(code=200, message="{} has been deleted".format(uargs.get("filename")))
        else:
            raise HTTPError(404, reason='{0} not found'.format(uargs.get("filename")))

    def post(self, *args, **kargs):
        uargs = self.payload()
        filename = uargs.get("filename")
        node = path.abspath(path.join(self.application.options.zkroot, \
                   urlsafe_b64encode(filename)))
        data = self.application.zk.ensure_path(node.decode())
        self.jsonify(code=200, message="{} has been created".format(data))


class RuleHandler(RestfulMixin, RequestHandler):

    def delete(self, *args, **kargs):
        uargs = self.payload()
        filename = uargs.get("filename")
        rulename = uargs.get("rulename")
        sing = False
        for file in self.application.zk.get_children(self.application.options.zkroot.decode()):
            node = path.abspath(path.join(self.application.options.zkroot, \
                   file))
            for rule in self.application.zk.get_children(node):
                if rulename == rule and urlsafe_b64encode(filename) == file:
                    node = path.abspath(path.join(self.application.options.zkroot, \
                            urlsafe_b64encode(filename), rulename))
                    self.application.zk.delete(node, recursive=True)
                    sing = True
            if sing:
                self.jsonify(code=200, message="{} rule has been deleted".format(rulename))
                break
        else:
            raise HTTPError(404, reason="{} rule not exists".format(rulename))     

    def post(self, *args, **kargs):
        uargs = self.payload()
        filename = uargs.get("filename")
        rules = uargs.get("rule")
        rulename = rules.get("name")
        for file in self.application.zk.get_children(self.application.options.zkroot.decode()):
            node = path.abspath(path.join(self.application.options.zkroot, \
                   file))
            for rule in self.application.zk.get_children(node):
                if rulename == rule:
                    raise HTTPError(404, reason="{} rule already exists".format(rule))
            if file == urlsafe_b64encode(filename):
                node = path.abspath(path.join(self.application.options.zkroot, \
                        urlsafe_b64encode(filename), rulename))
                data = self.application.zk.create(node, json.dumps(rules))
                if data:
                    self.jsonify(code=200, message="{} rule has been created".format(rulename))
                break
        else:
            raise HTTPError(404, reason="{} without this path".format(filename))

    def put(self, *args, **kargs):
        uargs = self.payload()
        filename = uargs.get("filename")
        rules = uargs.get("rule")
        rulename = rules.get("name")
        sing = False
        for file in self.application.zk.get_children(self.application.options.zkroot.decode()):
            node = path.abspath(path.join(self.application.options.zkroot, \
                   file))
            for rule in self.application.zk.get_children(node):
                if rulename == rule and urlsafe_b64encode(filename) == file:
                    node = path.abspath(path.join(self.application.options.zkroot, \
                            urlsafe_b64encode(filename), rulename))
                    data = self.application.zk.set(node, json.dumps(rules))
                    if data:
                        sing = True
            if sing:
                self.jsonify(code=200, message="{} rule has been updated".format(rulename))
                break
        else:
            raise HTTPError(404, reason="{} rule not exists".format(rulename))
