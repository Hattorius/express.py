from express import express

app = express()


def middleware(req, res, next):
    req.hi = "hello"
    next()
    print("This runs afterwards")

def anotherMiddleware(req, res, next):
    print("Does nothing")


@app.get("/", None, middleware, anotherMiddleware)
def helloWorld(req, res):
    res.send(req.hi)


app.listen(3000)