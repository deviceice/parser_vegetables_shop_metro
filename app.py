from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import Request
from pydantic import BaseModel
import uvicorn
import string
import random

url_storage = {}
url_length = 6
default_url = 'http://127.0.0.1:8000/'
app = FastAPI()


# Все в одном файле, смысле нет раскидывать такое маленькое api
# ____________________________________________________________________

# Типо models.py)
class OriginalUrl(BaseModel):
    original_url: str


def generate_short_url() -> str:
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(url_length))
    return short_url


request_count = {}


@app.middleware("http")
async def limit_requests(request: Request, next_call):
    ip_client = request.client.host
    request_count[ip_client] = request_count.get(ip_client, 0) + 1
    if request_count[ip_client] > 1:
        return HTTPException(status_code=429, detail="Слишком много запросов") # на локалке сам себя забанит)
    response = await next_call(request)
    return response


@app.post("/add_short_link/")
async def shorten_url(url_request: OriginalUrl):
    if url_request.original_url in url_storage.values():
        for short, original in url_storage.items():
            if original == url_request.original_url:
                return {"short_url": f"{default_url}{short}"}

    short_url = generate_short_url()
    while short_url in url_storage:
        short_url = generate_short_url()

    url_storage[short_url] = url_request.original_url
    return {"full_short_url": f"{default_url}{short_url}", 'base_url': default_url, 'short_url': short_url}


@app.get("/{short_url}")
async def redirect_to_original(short_url: str):    
    original_url = url_storage.get(short_url)
    print(original_url)
    if original_url:
        return RedirectResponse(f"{original_url}")
    else:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")


# типо main)
if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)
