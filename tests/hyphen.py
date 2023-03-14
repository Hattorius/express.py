from express import express

app = express()


@app.get("/flights/:from-:to")
def get(req, res):
    res.send(req.params)

app.listen(3000)