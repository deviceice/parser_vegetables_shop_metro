from fastapi import FastAPI, Request

app = FastAPI()
host = '127.0.0.1'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=host, port=8001)
