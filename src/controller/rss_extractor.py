import json
import feedparser
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.model.article import Article
from src.model.rss_feed import RSSFeed

class RSSExtractor():

    def get_feeds(self) -> list[RSSFeed]:
        with open('rss_urls.json') as f:
            data = json.load(f)
        return [RSSFeed(**feed) for feed in data]
    
    def get_articles(self, feeds: list[RSSFeed]) -> list[Article]:
        articles = []
        for feed in feeds:
            parsed = feedparser.parse(feed.url)
            for entry in parsed.entries:
                article = Article(
                    title=entry.get('title', None),
                    publication_date=entry.get('published', None),
                    url=entry.get('link', None),
                    image_url=entry.get('media_content', [{}])[0].get('url', None) if entry.get('media_content') else None,
                    description=entry.get('summary', None),
                    category=feed.category
                )
                articles.append(article)
        return articles

extractor = RSSExtractor()
feeds = extractor.get_feeds()
articles = extractor.get_articles(feeds)

print("FEEDS", feeds)
print("ARTICLES", articles)