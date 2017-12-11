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
import subprocess
import sys

class S(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        if self.path == '/oscap':
            print >>sys.stderr, 'INFO: Starting OpenSCAP scan.'
            subprocess.check_call("ssh target@target-app-server 'oscap xccdf eval --profile nist-800-171-cui  --fetch-remote-resources --results scan-results.xml /usr/share/xml/scap/ssg/content/ssg-centos7-xccdf.xml || oscap xccdf generate report scan-results.xml > /tmp/scan-report.html'", shell=True)
            self._set_headers()
            self.wfile.write("OK")
            print >>sys.stderr, 'INFO: OpenSCAP scan complete.'
            return

        if self.path == '/port-scan':
            print >>sys.stderr, 'INFO: Starting port scan.'
            (status,output) = commands.getstatusoutput("nmap target-app-server -p- -sT")
            self._set_headers()
            self.wfile.write("```\n%s\n```" % output)
            print >>sys.stderr, 'INFO: Port scan complete.'
            return

        print >>sys.stderr, 'WARNING: Received invalid HTTP request.'
        self._set_headers(404)
        self.wfile.write("Invalid URL.\n")

    def do_HEAD(self):
        print >>sys.stderr, 'INFO: Received HTTP HEAD request.'
        self._set_headers()

    def do_POST(self):
        print >>sys.stderr, 'WARNING: Received invalid HTTP request.'
        self._set_headers(405)
        self.wfile.write("POST method not allowed.")

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print >>sys.stderr, 'INFO: Security and Monitoring Server is fully up and running.'
    httpd.serve_forever()
    print >>sys.stderr, 'INFO: Security and Monitoring Server exiting.'

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
