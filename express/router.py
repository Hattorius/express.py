class Router:
    def __init__(self, app, route, routerid):
        self.app = app
        self.route = route
        self.routerid = routerid
        self.middleware = {}

    def _route(self, method, route, fun, *middleware):
        if self.route[-1] == "/" and route[0] == "/":
            route = route[1:]
        route = self.route + route
        return self.app.route(method, route, fun, *middleware, self.routerid)
    
    def get(self, route, fun = None, *middleware):
        return self._route("GET", route, fun, *middleware)

    def post(self, route, fun = None, *middleware):
        return self._route("POST", route, fun, *middleware)

    def head(self, route, fun = None, *middleware):
        return self._route("HEAD", route, fun, *middleware)

    def put(self, route, fun = None, *middleware):
        return self._route("PUT", route, fun, *middleware)

    def delete(self, route, fun = None, *middleware):
        return self._route("DELETE", route, fun, *middleware)

    def patch(self, route, fun = None, *middleware):
        return self._route("PATCH", route, fun, *middleware)
    
    def all(self, route, fun = None, *middleware):
        return self._route("*", route, fun, *middleware)
    
    def use(self, fun, path = "/*"):
        if self.route[-1] == "/" and path[0] == "/":
            path = path[1:]

        if "*" in path:
            path.replace("*", "(.*)")

        try:
            self.middleware[self.route + path].append(fun)
        except:
            self.middleware[self.route + path] = [fun]