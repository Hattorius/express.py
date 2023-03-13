from express import express


app = express()


def get(request, response):
    print(request.method, request.fullUrl)
    print("Cookies: ", request.cookies)
    print("Parameters: ", request.params)
    print("Host: ", request.host)

    response.append("Hi", "hello")
    response.send("Hello World!")

def redirectToComment(request, response):
    response.redirect("comment")

def serveFile(request, response):
    response.sendFile("start.py")

app.get("/", get)
app.get("/:userId/:postId/comment", get)
app.get("/:userId/:postId/", redirectToComment)
app.get("/file", serveFile)

app.listen()