from fastapi import FastAPI
app = FastAPI()
from data import main
from comments import comments_analysis
from test_script import testMain

@app.get("/")
def main_api():
    return {
        "message":"hello World"
    }

@app.get("/datos")
def get_data(URL:str=None):
    data = main(mainURL=URL)
    
    return{
        "items":data
    }

@app.get("/datosV2")
def test():
    data = testMain()
    
    return{
        "items":data
    }