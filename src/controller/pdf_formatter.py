from reportlab.platypus import Paragraph, SimpleDocTemplate, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from bs4 import BeautifulSoup
import requests
from io import BytesIO
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.controller.rss_extractor import RSSExtractor
from src.model.article import Article

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PdfFormatter():

    def get_article_image(self, article: Article) -> Image:
        logger.debug('get_article_image %s', getattr(article, 'image_url', None))
        if not getattr(article, 'image_url', None):
            return None
        try:
            r = requests.get(article.image_url, timeout=5)
            r.raise_for_status()
            bio = BytesIO(r.content)
            bio.seek(0)
            ir = ImageReader(bio)
            iw, ih = ir.getSize()
            if not ih:
                return None
            desired_height = 5*cm
            scale = desired_height / ih
            width = iw * scale
            bio.seek(0)
            logger.debug('downloaded image %s (%d bytes) original size %sx%s scaled to %sx%s', article.image_url, len(r.content), iw, ih, width, desired_height)
            return Image(bio, width=width, height=desired_height)
        except Exception:
            logger.exception('failed to get image')
            return None

    def get_article_content(self, article: Article) -> list[str]:
        try:
            logger.debug('fetching article url %s', article.url)
            r = requests.get(article.url, timeout=5)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            blocks = []
            for art in soup.find_all('article'):
                for tag in art.find_all(['p', 'h1', 'h2', 'h3']):
                    text = tag.get_text(strip=True)
                    if text:
                        blocks.append(text)
            logger.debug('extracted %d text blocks from %s', len(blocks), article.url)
            return blocks
        except Exception:
            logger.exception('failed to fetch article content %s', article.url)
            return []

    def build_article(self, article: Article) -> list:
        logger.debug('build_article %s', article.title)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(article.title or '', styles['Heading2']))
        if getattr(article, 'description', None):
            story.append(Paragraph(article.description or '', styles['Heading4']))
        img = self.get_article_image(article)
        if img:
            story.append(Spacer(1, 0.5*cm))
            story.append(img)
            story.append(Spacer(1, 0.5*cm))
        for blk in self.get_article_content(article):
            story.append(Paragraph(blk, styles['Normal']))
            story.append(Spacer(1, 0.2*cm))

        story.append(Spacer(1, 1*cm))
        return story

    def build(self, articles: list[Article], output_path: str):
        logger.debug('build pdf %s with %d articles', output_path, len(articles))
        doc = SimpleDocTemplate(output_path)
        story = []
        for article in articles[:2]:
            story.extend(self.build_article(article))
        doc.build(story)
        logger.debug('pdf written %s', output_path)


extractor = RSSExtractor()
feeds = extractor.get_feeds()
articles = extractor.get_articles(feeds)

path = "output/output_articles.pdf"
formatter = PdfFormatter()
formatter.build(articles, path)