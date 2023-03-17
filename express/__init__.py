import socket, re, traceback

from express.request import Request
from express.response import Response
from express.router import Router


class express:
    def __init__(self, bytes_to_receive=2048):
        self.bytes_to_receive = bytes_to_receive
        self.routes = {
            "GET": [],
            "HEAD": [],
            "POST": [],
            "PUT": [],
            "DELETE": [],
            "PATCH": [],
            "*": []
        }
        self.routers = []
        self.globalMiddleware = {}

    def _route(self, method, route, fun, middleware = (), router = None):
        middleware = list(middleware)
        originalRoute = "" + route

        if len(middleware) > 0 and type(middleware[-1]) is int:
            router = middleware[-1]
            middleware.pop()

        route = route.replace(".", "\.")
        route = route.replace("*", ".+")

        matches = []
        parts = route.split("/")
        for part in parts:
            while True:
                found = re.search("(:[^-.]*)", part)

                if not found:
                    break

                name = found.group(0).split(":")[1]
                if name in matches:
                    print(traceback.format_exc())
                    print("Method: %s" % method)
                    print("Route: %s" % originalRoute)
                    print("Parameter: %s" % name)
                    raise Exception("You've got multiple parameters with the same name!")

                originalName = "" + name
                regex = "(.+)"
                if "(" in name and ")" in name:
                    name, rest = name.split("(")
                    regex = "(" + rest

                route = route.replace(":" + originalName, regex)
                matches.append(name)

                part = part.replace(":" + originalName, "")

        route = f"^{route}$"

        try:
            self.routes[method].append({
                "route": route,
                "fun": fun,
                "middleware": middleware,
                "matches": matches,
                "router": router
            })
        except:
            self.routes[method] = [{
                "route": route,
                "fun": fun,
                "middleware": middleware,
                "matches": matches,
                "router": router
            }]

    def _listen(self, port, backlog):
        
        if socket.has_dualstack_ipv6():
            self.socket = socket.create_server(("", port), family=socket.AF_INET6, dualstack_ipv6=True)
        else:
            self.socket = socket.create_server(("", port))

        self.socket.listen(backlog)

        while True:
            client_socket, client_address = self.socket.accept()

            chunks = []
            while True:
                data = client_socket.recv(self.bytes_to_receive)
                chunks.append(data)

                if len(data) < self.bytes_to_receive : break

            data = b"".join(chunks).decode("utf-8")
            if len(data) == 0:
                client_socket.close()
                continue
            
            self.handleConnection(client_socket, data, client_address)

    def listen(self, port=8080, backlog=10):
        while True:
            try:
                self._listen(port, backlog)
            except Exception as e:
                print(traceback.format_exc())
                print("Error!")
                print(e)
                pass

    def notFound(self, response):
        response.status_code = 404
        response.end()

    def error(self, response):
        if not response.headersSent:
            response.status_code = 500
            response.end()

    def runMiddleware(self, middleware, request, response):
        try:
            res = middleware(request, response)
            if res is False:
                return False
            return True
        except Exception as e:
            print(traceback.format_exc())
            print("Error!")
            print(e)
            self.error(response)
            return False

    def runMiddlewaresAndEndpoint(self, middlewares, endpoint, request, response):
        def next():
            if response.headersSent:
                return

            if request.middlewareCount < len(middlewares):
                request.middlewareCount += 1
                currentCount = request.middlewareCount
                middlewares[request.middlewareCount - 1](request, response, next)
                
                if currentCount == request.middlewareCount:
                    next()
            else:
                request.middlewareCount += 1
                endpoint(request, response)
        
        next()

    def handleConnection(self, socket, data, client_address):
        request = Request(self, data, client_address)
        response = Response(self, socket, request)
        
        if not request.found:
            return self.notFound(response)

        middlewareToRun = []
        
        for middleware in self.globalMiddleware:
            if re.match(middleware, request.url):
                for func in self.globalMiddleware[middleware]:
                    middlewareToRun.append(func)

        if request.router is not None:
            router = self.routers[request.router]
            for middleware in router.middleware:
                if re.match(middleware, request.url):
                    for func in router.middleware[middleware]:
                        middlewareToRun.append(func)
        
        self.runMiddlewaresAndEndpoint(middlewareToRun + request.middleware, request.fun, request, response)

        if not response.headersSent:
            response.end()

    def route(self, method, route, fun, *middleware, router = None):
        if callable(middleware):
            middleware = [middleware]

        if fun is None:
            def get(function):
                self._route(method, route, function, middleware=middleware, router = router)
                return function
            return get
        self._route(method, route, fun, middleware=middleware, router = router)

    def get(self, route, fun = None, *middleware):
        return self.route("GET", route, fun, *middleware)

    def post(self, route, fun = None, *middleware):
        return self.route("POST", route, fun, *middleware)

    def head(self, route, fun = None, *middleware):
        return self.route("HEAD", route, fun, *middleware)

    def put(self, route, fun = None, *middleware):
        return self.route("PUT", route, fun, *middleware)

    def delete(self, route, fun = None, *middleware):
        return self.route("DELETE", route, fun, *middleware)

    def patch(self, route, fun = None, *middleware):
        return self.route("PATCH", route, fun, *middleware)
    
    def all(self, route, fun = None, *middleware):
        return self.route("*", route, fun, *middleware)
    
    def router(self, route):
        routerId = len(self.routers)
        router = Router(self, route, routerId)
        self.routers.append(router)
        return router
    
    def use(self, fun, path = "/*"):
        if "*" in path:
            path.replace("*", "(.*)")

        try:
            self.globalMiddleware[path].append(fun)
        except:
            self.globalMiddleware[path] = [fun]