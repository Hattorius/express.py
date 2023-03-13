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


def someMiddleware(request, response):
    request.hi = "Hello"

app.get("/", get, someMiddleware)
app.get("/:userId/:postId/comment", get, someMiddleware)
app.get("/:userId/:postId/", redirectToComment)
app.get("/file", serveFile)
app.get("/bad", badRequest)

app.listen()