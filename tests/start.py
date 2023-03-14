from express import express


app = express()


def get(request, response):
    print(request.method, request.fullUrl)
    print("Cookies: ", request.cookies)
    print("Parameters: ", request.params)
    print("Host: ", request.host)

    response.append("Hi", request.hi)
    response.send("Hello World!")

def redirectToComment(request, response):
    response.redirect("comment")

def serveFile(request, response):
    response.sendFile("start.py")

def badRequest(request, response):
    response.status(400).send("Bad Request!")

def omgitspost(request, response):
    response.send("hi")


def someMiddleware(request, response):
    request.hi = "Hello"

def theOtherMiddleware(request, response):
    request.hi = "No"

app.get("/", get, someMiddleware)
app.get("/:userId/:postId/comment", get, someMiddleware)
app.get("/:userId/:postId/", redirectToComment)
app.get("/file", serveFile)
app.get("/bad", badRequest)
app.post("/", omgitspost)

app.all("/hihi", omgitspost)

@app.get("/hello")
def hello(request, response):
    response.send("hi")

@app.get("/test", None, someMiddleware)
@app.head("/test", None, someMiddleware)
def test(request, response):
    response.append("Hi", request.hi)
    response.send("Hiii!!!")


appRouter = app.router("/user")

@appRouter.get("")
@appRouter.get("/")
@appRouter.get("/cheese")
def omg(request, response):
    response.append("Hi", request.hi)
    response.send("omg!!!")

appRouter.use(theOtherMiddleware)
appRouter.use(someMiddleware, "/cheese")

app.listen()