from pydantic import BaseModel


class OriginalUrl(BaseModel):
    original_url: str
