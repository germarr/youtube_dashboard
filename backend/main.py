from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def main_api():
    return {
        "message":"hello World"
    }