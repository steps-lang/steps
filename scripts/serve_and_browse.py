"""Run a web server for a given directory and open a browser."""
import http.server
import multiprocessing
import socketserver
import sys
import webbrowser


PORT = 8000
ADDR = '127.0.0.1'
PATH = 'index.html'
 
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Request handler that sets the path to a given directory.

    :param path: the path to the directory which should be served.
    :type path: str
    """
    def do_GET(self) -> http.server.SimpleHTTPRequestHandler:
        """Implement the get method."""
        self.path = PATH 
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


class Server(multiprocessing.Process):
    """Process running the HTTP server."""
    def run(self):
        """Override the ``run`` method."""
        print("HTTP Server starts.")
        Handler = MyHttpRequestHandler
 
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("Http Server Serving at port", PORT)
            try:
                httpd.serve_forever()
            except (KeyboardInterrupt, SystemExit):
                print("HTTP Server stopped.")


if __name__ == '__main__':
    PATH = sys.argv[1]
    httpd = Server()
    try:
        httpd.start()
        webbrowser.open(f'http://{ADDR}:{PORT}')
        httpd.join()
    except (KeyboardInterrupt, SystemExit):
        pass
    print('End')

