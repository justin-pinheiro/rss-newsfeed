import json
import feedparser
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.model.article import Article
from src.model.rss_feed import RSSFeed

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RSSExtractor():

    def get_feeds(self) -> list[RSSFeed]:
        logger.debug('loading feeds from rss_urls.json')
        with open('rss_urls.json') as f:
            data = json.load(f)
        feeds = [RSSFeed(**feed) for feed in data]
        logger.debug('loaded %d feeds', len(feeds))
        return feeds
    
    def get_articles(self, feeds: list[RSSFeed]) -> list[Article]:
        articles = []
        for feed in feeds:
            logger.debug('parsing feed %s', feed.url)
            parsed = feedparser.parse(feed.url)
            entries = getattr(parsed, 'entries', [])
            logger.debug('found %d entries in feed %s', len(entries), feed.name)
            for entry in entries:
                article = Article(
                    title=entry.get('title', None),
                    publication_date=entry.get('published', None),
                    url=entry.get('link', None),
                    image_url=entry.get('media_content', [{}])[0].get('url', None) if entry.get('media_content') else None,
                    description=entry.get('summary', None),
                    category=feed.category
                )
                articles.append(article)
        logger.debug('extracted total %d articles', len(articles))
        return articles