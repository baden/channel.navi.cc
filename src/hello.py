import tornado.ioloop
import tornado.web
import os
import platform
from datetime import datetime
#import pymongo
from pymongo import Connection
import config

db = Connection(config.MONGO_URL).baden_test
fake = db["fake"]

inmemcounter = 0
startedat = datetime.utcnow()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global inmemcounter, startedat
        inmemcounter += 1
        self.write("""
            <h2>Its worked!</h2>
            <p><b>DB:</b> %s</p>
            <p><b>COL:</b> %s</p>
            <p><b>Started at:</b> %s</p>
            <p><b>Global counter:</b> %d</p>
            """ % (repr(db), repr(fake), str(startedat), inmemcounter))

        fall = fake.find_one({"_id": "counter"})
        if fall is None:
            fall = {"_id": "counter", "value": 0}
        else:
            fall["value"] += 1
        self.write("<p><b>Mongo counter:</b> %s</p>" % repr(fall["value"]))
        fake.save(fall)

        self.write("<h2>Platform information</h2>")
        self.write("<p><b>System:</b> %s</p>" % platform.system())
        self.write("<p><b>Release:</b> %s</p>" % platform.release())
        self.write("<p><b>Version:</b> %s</p>" % platform.version())
        self.write("<p><b>Machine:</b> %s</p>" % platform.machine())
        self.write("<p><b>Processor:</b> %s</p>" % platform.processor())
        self.write("<p><b>Node:</b> %s</p>" % platform.node())
        self.write("<p><b>Python:</b> %s</p>" % platform.python_version())
        self.write("<p><b>Port:</b> %s</p>" % os.environ.get('PORT', 5000))

        self.write("<h2>Memory information</h2>")
        for m in open('/proc/meminfo'):
            self.write("<p>%s</p>" % m)


uname = os.uname()
debug = False
if uname[1] == 'BigBrother':
    debug = True

application = tornado.web.Application([
    (r"/", MainHandler),
], debug=debug)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # For direct: web: python hello.py
    #port = 18888  # For gunicorn: web: ./bin/gunicorn -k tornado --workers=4 --bind=0.0.0.0:$PORT hello
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
