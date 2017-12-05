#!/usr/bin/env python
"""
Adapted from "Very simple HTTP server in python" <https://gist.github.com/bradmontgomery/2219997>

Written for Python 2.

Usage:
    ./scan-http-daemon.py [<port>]
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import commands

class S(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        (status,output) = commands.getstatusoutput("ssh target@target-app-server 'oscap xccdf eval --profile nist-800-171-cui  --fetch-remote-resources --results scan-results.xml /usr/share/xml/scap/ssg/content/ssg-centos7-xccdf.xml || oscap xccdf generate report scan-results.xml || cat scan-results.xml'")
        self._set_headers()
        self.wfile.write("Status: %s\n\n%s\n" % (status, output))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers(405)
        self.wfile.write("POST method not allowed.")

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
