import socket
import tkinter
import sys
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
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            self.canvas.create_text(x, y - self.scroll, text=c)


    def load(self, url):
        body = URL(url).request()
        text = URL.show(body)
        self.display_list = layout(text)
        self.draw()


    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()


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
        response_headers = {}
        # Note: Headers are case-insensitive and white-spaces are insignificant in HTTP header
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

    @staticmethod
    def show(body):

        text = ""

        # in_tag -> when is currently between a pair of angle brackets
        in_tag = False

        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                text += c

        return text




def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP

        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP

    return display_list

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python browser.py <URL>")
        sys.exit(1)

    browser = Browser()
    url = sys.argv[1]
    browser.load(url)
    browser.window.mainloop()
