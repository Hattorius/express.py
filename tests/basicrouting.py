from express import express


app = express()

@app.get("/")
def helloWorld(req, res):
    res.send("Hello World!")

@app.post("/")
def aPostRequest(req, res):
    res.send("Got a POST request")

@app.put("/user")
def updateUser(req, res):
    res.send("Got a PUT request at /user")


def deleteUser(req, res):
    res.send("Got a DELETE request at /user")
app.delete("/user", deleteUser)


app.listen(3000)