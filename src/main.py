import socket
import tkinter
from settings import *

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()


        # self.canvas.create_rectangle(10, 20, 400, 300)

class URL:

    def __init__(self, url):

        if "://" not in url:
            url = "http://" + url # # Default to "http://" if no scheme provided

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url


    def request(self):
        # Create a socket
        s = socket.socket(
            family = socket.AF_INET,
            type= socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        # Host and Port
        s.connect((self.host, 80))

        # Make a request
        s.send(("GET {} HTTP/1.0\r\n".format(self.path) +
                "Host: {}\r\n\r\n".format(self.host)) \
                    .encode("utf8")) # \r\n instead of \n for newlines
        # Receive the response
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        # Status
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        # Headers
        # Note: Headers are case-insensitive and white-spaces are insignificant in HTTP header
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.split() # array, max

            # Check if the data we are trying to access are not sent in an unusual way
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

        # Body
        body = response.read()
        s.close()
        return body


    def show(self, body):

        self.text = ""

        # in_tag -> when is currently between a pair of angle brackets
        in_tag = False

        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                self.text += c

        return self.text


    def load(self, canvas):
        body = self.request()
        self.show(body)

        # x, y = 100, 100
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in self.text:
            canvas.create_text(cursor_x , cursor_y, text=c)
            cursor_x += HSTEP

            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP

if __name__ == "__main__":
    import sys

    browser = Browser()
    url_instance = URL(sys.argv[1])
    url_instance.load(browser.canvas)
    browser.window.mainloop()
