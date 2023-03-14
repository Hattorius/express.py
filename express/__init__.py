import socket, re

from express.request import Request
from express.response import Response


class express:
    def __init__(self, bytes_to_receive=2048):
        self.bytes_to_receive = bytes_to_receive
        self.routes = {
            "GET": [],
            "HEAD": [],
            "POST": [],
            "PUT": [],
            "DELETE": [],
            "PATCH": []
        }

    def _route(self, method, route, fun, *middleware):
        originalRoute = "" + route

        matches = []
        parts = route.split("/")
        for part in parts:
            if re.match("^:.+$", part):
                name = part.split(":")[1]

                if name in matches:
                    print("Method: %s" % method)
                    print("Route: %s" % originalRoute)
                    print("Parameter: %s" % name)
                    raise Exception("You've got multiple parameters with the same name!")

                route = route.replace(part, "(.+)")
                matches.append(name)

        route = f"^{route}$"

        self.routes[method].append({
            "route": route,
            "fun": fun,
            "middleware": list(middleware),
            "matches": matches
        })

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

    def handleConnection(self, socket, data, client_address):
        request = Request(self, data, client_address)
        response = Response(self, socket, request)
        
        if not request.found:
            return self.notFound(response)

        # run middleware
        continue_to_route = True
        for middleware in request.middleware:
            try:
                res = middleware(request, response)
                if res is False:
                    continue_to_route = False
                    break
            except Exception as e:
                print("Error!")
                print(e)
                return self.error(response)
        
        if continue_to_route:
            try:
                request.fun(request, response)
            except Exception as e:
                print("Error!")
                print(e)
                return self.error(response)

        if not response.headersSent:
            response.end()

    def route(self, method, route, fun, *middleware):
        if callable(middleware):
            middleware = [middleware]

        if fun is None:
            def get(function):
                self._route(method, route, function, *middleware)
            return get
        self._route(method, route, fun, *middleware)

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