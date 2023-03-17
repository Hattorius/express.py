import time
from express import express

app = express()

def requestTime(req, res, next):
    req.requestTime = time.time()
    next()
    print(f"Request handling took {time.time() - req.requestTime} seconds")

@app.get("/", None, requestTime)
def home(req, res):
    res.send(f"Requested at: {req.requestTime}")

app.listen(3000)