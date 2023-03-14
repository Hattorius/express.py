import re, json

from express.helpers import url_parse


class Headers(dict):
    pass

class Params(dict):
    pass

class Cookies(dict):
    pass

class Request:
    def __init__(self, app, data, client_address):
        self.app = app
        self.ip = client_address[0]

        splitted = data.split('\r\n\r\n', 1)
        headers = splitted[0]
        self.body = ""
        if len(splitted) > 1:
            self.body = splitted[1]
        self.json = None
        headers = headers.split("\r\n")

        header = headers[0].split(" ")
        headers.pop(0)

        self.method = header[0]
        self.originalUrl = url_parse(header[1])
        self.protocol = header[2]
        self.ips = []
        self.url = self.originalUrl.split("?")[0]
        self.path = "/" + self.url.split("/")[-1]
        self.baseUrl = "/" + self.url.split(self.path)[0]
        self.subdomains = []
        self.fullUrl = "" + self.originalUrl

        # Headers into dictionaries
        self.headers = Headers()
        self.cookies = Cookies()
        for item in headers:
            name, value = item.split(": ", 1)

            if name == "Host":
                self.host = value
                self.domain = value.split(":")[0]
                self.subdomains = self.domain.split(".")[:-2]

                self.fullUrl = value + self.fullUrl

            if name == "X-Forwarded-For":
                self.ips = [ip.strip() for ip in value.split(",")]

            if name == "Cookie":
                for cookieName, cookieValue in [cookie.split("=", 1) for cookie in value.split("; ")]:
                    self.cookies[cookieName] = cookieValue
                    setattr(self.cookies, cookieName, cookieValue)

            self.headers[name] = value
            setattr(self.headers, name, value)

        # Find route in list
        self.found = False
        for route in app.routes[self.method] + app.routes["*"]:
            if re.match(route["route"], self.url):
                self.found = True
                self.fun = route["fun"]
                self.middleware = list(route["middleware"])
                self.matches = list(route["matches"])
                self.matchRoute = route["route"]

        # Put parameters in url in dictionary
        self.params = Params()
        if self.found:
            for i, item in enumerate(re.search(self.matchRoute, self.url).groups()):
                self.params[self.matches[i]] = item
                setattr(self.params, self.matches[i], item)

    def json(self):
        if self.json is None:
            self.json = json.loads(self.body)
        return self.json

    def header(self, name):
        try:
            return self.headers[name]
        except:
            return None
        
    def param(self, name):
        try:
            return self.params[name]
        except:
            return None
        
    def cookie(self, name):
        try:
            return self.cookies[name]
        except:
            return None
        
    def get(self, name):
        for header in self.headers:
            if header.lower() == name.lower():
                return self.headers[header]
            
        return None
        
    def acceptCheck(self, name, header):
        if "*" in name:
            name = name.replace("*", ".+")

        accept = self.get(header)
        if accept is None:
            return None
        
        accepts = [accept.strip() for accept in accept.split(";")[0].split(",")]
        for accept in accepts:
            res = re.search(name, accept)
            return res.group(0)
        
        return False

    def accepts(self, name):
        return self.acceptCheck(name, "Accept")
    
    def acceptsCharsets(self, name):
        return self.acceptCheck(name, "Accept-Charset")
    
    def acceptsEncodings(self, name):
        return self.acceptCheck(name, "Accept-Encoding")
    
    def acceptsLanguages(self, name):
        return self.acceptCheck(name, "Accept-Language")
    
    def isContentType(self, name):
        return self.acceptCheck(name, "Content-Type")