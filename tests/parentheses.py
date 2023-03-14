from express import express

app = express()


@app.get("/user/:userId(\d+)")
def get(req, res):
    res.send(req.params)

app.listen(3000)