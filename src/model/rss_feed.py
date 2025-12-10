
from dataclasses import dataclass

@dataclass
class RSSFeed():
    name: str
    category: str
    url: str