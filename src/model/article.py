
from dataclasses import dataclass

@dataclass
class Article():
    title: str
    publication_date: str
    url: str
    image_url: str
    description: str
    category: str