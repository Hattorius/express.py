from express import express

app = express()


def middleware(req, res):
    req.hi = "hello"

@app.get("/", None, middleware)
def helloWorld(req, res):
    res.send(req.hi)


app.listen(3000)