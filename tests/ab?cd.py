from express import express

app = express()


@app.get("/ab?cd")
def get(req, res):
    res.send('ab?cd')

app.listen(3000)