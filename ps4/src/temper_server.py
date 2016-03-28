#! /usr/bin/env python

from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler
import struct
from datetime import datetime
import ssl
import sqlite3 as sqlite

SERVER_HOST = ""
SERVER_PORT = 1234

output_tmpl = "Time: %s" +\
    "\tHumidity: %.2f%%" +\
    "\tTemperature: %.2f*C %.2f*F" +\
    "\tHeat index: %.2f*C %.2f*F"


def print_datapoint(parts):
    """
    Print the datapoint to stdout
    :param parts: The parts of the datapoint as a tuple
    """
    t = datetime.fromtimestamp(parts[0])
    humid = parts[1]
    temp_c = parts[2]
    temp_f = parts[3]
    heat_c = parts[4]
    heat_f = parts[5]
    print output_tmpl % (t, humid, temp_c, temp_f, heat_c, heat_f)


def store_datapoint(sql, parts):
    """
    Store the datapoint in the Database.
    :param sql: A sqlite3 connection into the sqlite db
    :param parts: A tuple of the datapoint parts. See print_datapoint
    """
    t = datetime.fromtimestamp(parts[0])
    humid = parts[1]
    temp_c = parts[2]
    temp_f = parts[3]
    heat_c = parts[4]
    heat_f = parts[5]
    c = sql.cursor()
    c.execute("INSERT INTO points VALUES (?,?,?,?,?,?)",
        (t, humid, temp_c, temp_f, heat_c, heat_f))
    sql.commit()


class SSL_TCPServer(TCPServer):
    """
    Adds SSL to the SocketServer.  Based on response by WarriorPaw in
    http://stackoverflow.com/questions/8582766/adding-ssl-support-to-socketserver
    """
    def __init__(self,
                 server_address,
                 RequestHandlerClass,
                 certfile,
                 keyfile,
                 bind_and_activate=True):
        TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.certfile = certfile
        self.keyfile = keyfile

    def get_request(self):
        newsocket, fromaddr = self.socket.accept()
        connstream = ssl.wrap_socket(newsocket,
                                     server_side=True,
                                     certfile=self.certfile,
                                     keyfile=self.keyfile)
        return connstream, fromaddr

class SSL_ThreadingTCPServer(ThreadingMixIn, SSL_TCPServer):
    """
    This adds Threading to the SSL_TCPServer.
    """
    pass

class TempHandler(StreamRequestHandler):
    """
    This handler defines the server-side behavior for parsing a tcp stream.
    """
    def handle(self):
        """
        This handles a single TCP connection.  One is spawned for each new
        TCP stream.  When the function returns the connection closes.
        """
        try:
            conn = sqlite.connect("temp.db")
            while True:
                data = self.request.recv(48)
                if not data:
                    break
                parts = struct.unpack("dddddd", data)
                print_datapoint(parts)
                store_datapoint(conn, parts)
        except KeyboardInterrupt:
            pass
        finally:
            conn.close()

def prepare_db():
    """
    Make sure that the database exists and has the right schema.
    """
    conn = sqlite.connect("temp.db")
    sql = conn.cursor()
    sql.execute("SELECT sql FROM sqlite_master WHERE name='points'")
    rows = sql.fetchall()
    if len(rows) == 0:
        print "Database does not exist.  Creating Database..."
        sql.execute('''CREATE TABLE points
                    (date datetime, humidity real, temp_c real, temp_f real, index_c real, index_f)''')
        print "Database created"
    conn.close()

def main():
    prepare_db()
    server = SSL_ThreadingTCPServer((SERVER_HOST, SERVER_PORT),
                                    TempHandler,
                                    "server.cert",
                                    "server.key")
    server.serve_forever()


if __name__ == "__main__":
    main()
