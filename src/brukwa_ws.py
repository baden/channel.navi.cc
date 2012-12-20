# Demo application for brukva
# In order to use:
#  1. $ python app.py
#  2. Open in your browser that supports websockets: http://localhost:8888/
#     You should see text that says "Connected..."
#  3. $ curl http://localhost:8888/msg -d 'message=Hello!'
#     You should see 'Hello!' in your browser

import brukva
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop


c = brukva.Client()
c.connect()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html", title="Websocket test")


class NewMessage(tornado.web.RequestHandler):
    def post(self):
        message = self.get_argument('message')
        c.publish('test_channel', message)
        self.set_header('Content-Type', 'text/plain')
        self.write('sent: %s' % (message,))


class MessagesCatcher(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessagesCatcher, self).__init__(*args, **kwargs)
        self.client = brukva.Client()
        self.client.connect()
        self.client.subscribe('test_channel')

    def open(self):
        self.client.listen(self.on_message)

    def on_message(self, result):
        self.write_message(str(result.body))

    def close(self):
        self.client.unsubscribe('test_channel')
        self.client.disconnect()


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/msg', NewMessage),
    (r'/track', MessagesCatcher),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
