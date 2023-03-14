from express import express

app = express()


@app.get("/users/:userId/books/:bookId")
def get(req, res):
    res.send(req.params)

app.listen(3000)