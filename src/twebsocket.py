#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zmq.eventloop import ioloop
ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream
import zmq

from tornado import websocket
import tornado
import json

import cPickle as pickle


ctx = zmq.Context()


class WebHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html", title="My title")


class MainHandler(websocket.WebSocketHandler):
    _first = True

    @property
    def ref(self):
        return id(self)

    def initialize(self):
        print "WebSocket initialize"
        self.push_socket = ctx.socket(zmq.PUSH)
        self.sub_socket = ctx.socket(zmq.SUB)

        self.push_socket.connect("ipc:///tmp/ws_push")
        #self.sub_socket.connect("ipc:///tmp/ws_sub")
        self.sub_socket.bind("ipc:///tmp/ws_sub")
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.zmq_stream = ZMQStream(self.sub_socket)
        self.zmq_stream.on_recv(self.zmq_msg_recv)

    def open(self, *args, **kwargs):
        print "WebSocket opened", args, kwargs

    def on_message(self, message):
        print "WebSocket on_message"
        if self._first:
            msg = {'message': message, 'id':self.ref, 'action':'connect'}
            self._first = False

        else:
            msg = {'message': message, 'id':self.ref, 'action':'message'}

        self.push_socket.send_pyobj(msg)

    def on_close(self):
        print "WebSocket closed"
        msg = {'message': '', 'id': id(self), 'action': 'close'}
        self.push_socket.send_pyobj(msg)
        self.zmq_stream.close()
        self.sub_socket.close()
        self.push_socket.close()

    def zmq_msg_recv(self, data):
        print "zmq_msg_recv: %s" % repr(data)
        for message in data:
            message = pickle.loads(message)
            #_id, _msg = message['id'], message['message']

            print ' = ', repr(message)
            #if _id != self.ref:
            #    continue

            #self.write_message(_msg)
            self.write_message(json.dumps(message, indent=4))



application = tornado.web.Application([
    (r"/", WebHandler),
    (r"/socket", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
