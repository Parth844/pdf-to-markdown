from pydantic import BaseModel
from typing import List

class ParseResponse(BaseModel):
    markdown: str
    images: List[str]