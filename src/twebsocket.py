#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zmq.eventloop import ioloop
ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream
import zmq

#from tornado import websocket
import tornado
import json
import sockjs.tornado

import cPickle as pickle


clients = set()


class WebHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html", title="My title")


#class MainHandler(websocket.WebSocketHandler):
class SocketConnection(sockjs.tornado.SockJSConnection):

    def on_open(self, request):
        print "SocketJS opened:", repr(request.arguments)
        clients.add(self)

    def on_message(self, message):
        print 'on_message:%s' % str(message)
        #self.session.server.publish_stream.send_unicode(message)
        pass
        #self.push_socket.send_pyobj(msg)

    def on_close(self):
        print ':on_close'
        clients.remove(self)
    '''
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
    '''


ctx = zmq.Context()

#pub_socket = ctx.socket(zmq.PUB)
sub_socket = ctx.socket(zmq.SUB)

#pub_socket.connect("ipc:///tmp/ws_pub")
#self.sub_socket.connect("ipc:///tmp/ws_sub")
sub_socket.bind("ipc:///tmp/ws_sub")
sub_socket.setsockopt(zmq.SUBSCRIBE, "")

sub_stream = ZMQStream(sub_socket)
#zmq_stream.on_recv(zmq_msg_recv)


#        self.zmq_stream.close()
#        self.sub_socket.close()
#        self.push_socket.close()
#
SocketRouter = sockjs.tornado.SockJSRouter(SocketConnection, '/socket')
#SocketRouter.clients = clients
#SocketRouter.publish_stream = pub_stream


def on_receive_message(data):
    print 'on_receive_message:%s' % str(data)
    for message in data:
        message = pickle.loads(message)
        try:
            message = json.dumps(message, indent=4)
        except TypeError, e:
            message = json.dumps({"error": str(e), "dir": dir(e), "args": repr(e.args), "message": repr(e.message) })
        SocketRouter.broadcast(clients, message)

sub_stream.on_recv(on_receive_message)

application = tornado.web.Application([
    (r"/", WebHandler),
] + SocketRouter.urls)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
