from express import express

app = express()


@app.get("/random.text")
def helloWorld(req, res):
    res.send("Hello World!")

app.listen(3000)