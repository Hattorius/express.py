import time, json, os

from express.helpers import url_encode, timeToDate, getMIMEFromFileType, getStatusText


class Response:
    def __init__(self, app, socket, request):
        self.app = app
        self.socket = socket
        self.request = request
        self.headers = []
        self.status_code = 200
        self.status_text = None
        self.content_type = "text/html"

        self.headersSent = False

    def send(self, data=""):
        if self.headersSent:
            raise Exception("Headers were already sent, can't send again!")

        if self.status_text is None:
            self.status_text = getStatusText(self.status_code)

        if self.status_text is None:
            self.status(500).send()
            raise Exception("You must set a custom status text if the status code is custom")

        response = f"{self.request.protocol} {self.status_code} {self.status_text}\r\n"

        if type(data) is object:
            self.append("Content-Type", "application/json")
            data = json.dumps(data)
        data = str(data)

        self.append("Content-Length", len(("\r\n" + data).encode()))

        if self.get("Content-Type") is None:
            self.append("Content-Type", self.content_type)

        for header in self.headers:
            response += header[0] + ": " + header[1] + "\r\n"
        
        response += "\r\n"
        if self.request.method != "HEAD":
            response += "\r\n" + data

        self.socket.send(response.encode())
        self.socket.close()
        self.headersSent = True

    def status(self, status_code):
        self.status_code = status_code
        return self

    def _append(self, field, value):
        if type(value) is object:
            value = json.dumps(value)

        self.headers.append([str(field), str(value)])

    def append(self, field, value):
        if type(value) is list:
            for item in value:
                self._append(field, item)
            return self
        
        self._append(field, value)
        return self

    def get(self, name):
        for header in self.headers:
            if header[0].lower() == name.lower():
                return header[1]
            
        return None
    
    def cookie(self, name, value, options = {}):
        cookie = f"{name}={url_encode(value)}"
        if "encode" in options:
            cookie = f"{name}={options['encode'](value)}"
        
        if "domain" in options:
            cookie += f"; Domain={options['domain']}"

        if "expires" in options:
            cookie += f"; Expires={timeToDate((options['expires'] + time.time() * 1000) / 1000)}"

        if "maxAge" in options:
            cookie += f"; Max-Age={options['maxAge'] / 1000}"

        if "path" in options:
            cookie += f"; Path={options['path']}"

        if "secure" in options:
            cookie += f"; Secure"

        if "sameSite" in options:
            if type(options["sameSite"]) is bool:
                if options["sameSite"]:
                    cookie += "; Same-Site=Strict"
                else:
                    cookie += "; Same-Site=None; Secure"

            else:
                cookie += f"; Same-Site={options['sameSite']}"
                if options['sameSite'] == "None":
                    if "; Secure;" not in cookie:
                        cookie += f"; Secure"

        self._append("Set-Cookie", cookie)
        return self

    def clearCookie(self, name, options = {}):
        cookie = f"{name}="
        
        if "domain" in options:
            cookie += f"; Domain={options['domain']}"

        if "path" in options:
            cookie += f"; Path={options['path']}"

        if "secure" in options:
            cookie += f"; Secure"

        if "sameSite" in options:
            if type(options["sameSite"]) is bool:
                if options["sameSite"]:
                    cookie += "; Same-Site=Strict"
                else:
                    cookie += "; Same-Site=None; Secure"

            else:
                cookie += f"; Same-Site={options['sameSite']}"
                if options['sameSite'] == "None":
                    if "; Secure;" not in cookie:
                        cookie += f"; Secure"

        cookie += "; Max-Age=-1"

        self._append("Set-Cookie", cookie)
        return self

    def end(self):
        return self.send()

    def format(self, options, default=None):
        for format in options:
            if self.request.accepts(format):
                return options[format]()

        if default is None:
            return None
        
        return default()

    def json(self, body):
        self.append("Content-Type", "application/json")
        return self.send(json.dumps(body))

    def jsonp(self, body):
        self.append("Content-Type", "application/javascript")
        return self.send(f"callback({json.dumps(body)})")
    
    def location(self, location):
        if location != "back":
            return self.append("Location", location)

        referer = self.request.get("referer")
        if referer is not None:
            return self.append("Location", referer)

        return self.append("Location", "/")

    def redirect(self, statusOrPath, path = None):
        if path is None:
            path = "" + statusOrPath
            statusOrPath = 302

        if path[0] != "/":
            path = "http://" + "/".join(self.request.fullUrl.split("/")[:-1]) + "/" + path

        self.status_code = statusOrPath
        self.location(path)
        self.send()

    def sendFile(self, path, options = {}):
        type = path.split(".")[-1]
        mime = getMIMEFromFileType("." + type)

        self.append("Content-Type", mime)
        with open(path) as f:
            file = f.read()

        if ("cacheControl" in options and options["cacheControl"]) or "cacheControl" not in options:
            if "maxAge" in options:
                self.append("Cache-Control", f"max-age={options['maxAge'] / 1000}")
            else:
                self.append("Cache-Control", "max-age=no-cache")

        if "headers" in options:
            for header in options["headers"]:
                self.append(header, options["headers"][header])

        if "lastModified" not in options or options["lastModified"]:
            self.append("Last-Modified", timeToDate(os.path.getmtime(path)))


        return self.send(file)
