# type: ignore
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
from modified_queue import Queue


class S(SimpleHTTPRequestHandler):
    right_q = Queue(5)
    left_q = Queue(5)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        # <--- Gets the size of data
        content_length = int(self.headers['Content-Length'])
        # <--- Gets the data itself
        post_data = self.rfile.read(content_length)
        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #              str(self.path), str(self.headers), post_data.decode('utf-8'))
        # print(post_data.decode('utf-8'))
        post_data_split = post_data.decode('utf-8').split('&')[0:2]
        # print(post_data_split)
        if post_data_split[0][5] == 'r':
            if self.right_q.is_full():
                self.right_q.dequeue()
            self.right_q.enqueue(post_data_split[1][3:]+'\n')
            if float(post_data_split[1][3:]) > 0.80:
                right_raised = "Raised\n"
            else:
                right_raised = "Lowered\n"
            with open('right_side_status.txt', 'w') as right_f:
                right_f.writelines(self.right_q.get_items())
        
        if post_data_split[0][5] == 'l':
            if self.left_q.is_full():
                self.left_q.dequeue()
            self.left_q.enqueue(post_data_split[1][3:]+'\n')
            if float(post_data_split[1][3:]) > 0.80:
                left_raised = "Raised\n"
            else:
                left_raised = "Lowered\n"
            with open('left_side_status.txt', 'w') as right_f:
                right_f.writelines(self.left_q.get_items())

        # self._set_response()
        self.wfile.write("POST request for {}".format(
            self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
