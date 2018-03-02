#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer

import subprocess
import time


ftp_server_proc = None


def start_ftp_server(resp):
    global ftp_server_proc
    if ftp_server_proc is not None:
        stop_ftp_server(resp)
    resp.write(b'Opening port 21 on the target application server...\n\n')
    ftp_server_proc = subprocess.Popen("docker exec target-app-server python -m SimpleHTTPServer 21", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    resp.write(b'FTP server started...\n\n')
    try:
        ftp_server_proc.wait(2)
    except subprocess.TimeoutExpired:
        pass # still running, good
    if ftp_server_proc.returncode is not None:
        resp.write('FTP server terminated with code {}.\n\n'.format(ftp_server_proc.returncode).encode("utf8"))
        resp.write(ftp_server_proc.stdout.read())
        resp.write(ftp_server_proc.stderr.read())
        ftp_server_proc = None
    else:
        resp.write(b'FTP server is running.\n\n')


def stop_ftp_server(resp):
    global ftp_server_proc
    if ftp_server_proc is None:
        resp.write(b'FTP server is not running.\n\n')
        return
    resp.write(b'Terminating FTP server...\n\n')
    ftp_server_proc.kill()
    ftp_server_proc.wait(10)
    resp.write(b'FTP server terminated.\n\n')
    resp.write(ftp_server_proc.stdout.read())
    resp.write(ftp_server_proc.stderr.read())
    ftp_server_proc = None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            with open("index.html", "rb") as f:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f.read())
                return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Page not found.\n")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        if self.path == "/open-a-port":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                if ftp_server_proc is None:
                    start_ftp_server(self.wfile)
                else:
                    stop_ftp_server(self.wfile)
                return

        self.send_response(405)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"POST not allowed here.\n")

if __name__ == "__main__":
    httpd = HTTPServer(('', 80), Handler)
    import socket; httpd.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    httpd.serve_forever()
