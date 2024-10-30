from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import models
from
import string
import random



url_storage = {}
url_length = 6
default_url = 'http://127.0.0.1:8000/'

def generate_short_url() -> str:
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(url_length))
    return short_url


@app.post("/shorten/")
async def shorten_url(url_request: models.OriginalUrl):
    if url_request.original_url in url_storage.values():
        for short, original in url_storage.items():
            if original == url_request.original_url:
                return {"short_url": f"{default_url}{short}"}

    short_url = generate_short_url()
    while short_url in url_storage:
        short_url = generate_short_url()  # генерация уникальной link,  на случай совпадения

    url_storage[short_url] = url_request.original_url
    return {"full_short_url": f"{default_url}{short_url}", 'base_url': default_url, 'short_url': short_url}


@app.get("/{short_url}")
async def redirect_to_original(short_url: str):
    print(short_url)
    print(url_storage)
    original_url = url_storage.get(short_url)
    if original_url:
        return RedirectResponse(f"{original_url}")
    else:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
