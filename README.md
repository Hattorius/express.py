# [express.py](https://pypi.org/project/web-express-py/)
Python implementation of the widely used express.js

# Why
Going to answer this first: because yes. More out of boredom and wanting to do something with my time rather than playing games. But oh well, here it is.

# Installation
Install this package with a very very very very very simple command:
```sh
# Unix / macOS:
python3 -m pip install --upgrade web-express-py

# Windows:
py -3 -m pip install --upgrade web-express-py
```

After this, you can just import `express` into any of your projects using:
```py
from express import express
```

## Ok here comes stealing examples from express.js

# Hello world example
```py
from express import express

app = express()

@app.get("/")
def helloWorld(req, res):
    res.send("Hello World!")

app.listen(3000)
```

# Basic routing
```py
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
```

# More routing info
If you want to read **all** of the routing API through the guide???? [click here](https://github.com/Hattorius/express.py/wiki/Guide---Routing)