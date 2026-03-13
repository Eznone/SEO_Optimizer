import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List

class SitemapGenerator:
    """
    Generates an XML sitemap based on the Sitemaps.org protocol.
    """
    def __init__(self, urls: List[str], changefreq: str = "weekly", priority: float = 0.5):
        self.urls = urls
        self.changefreq = changefreq
        self.priority = str(priority)
        self.generation_time = datetime.now().strftime('%Y-%m-%d')

    def generate_xml(self) -> bytes:
        """
        Creates the XML structure for the sitemap and returns it as bytes.
        """
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        for url in self.urls:
            url_el = ET.SubElement(urlset, "url")
            ET.SubElement(url_el, "loc").text = url
            ET.SubElement(url_el, "lastmod").text = self.generation_time
            ET.SubElement(url_el, "changefreq").text = self.changefreq
            ET.SubElement(url_el, "priority").text = self.priority

        return ET.tostring(urlset, encoding='utf-8', method='xml', xml_declaration=True)