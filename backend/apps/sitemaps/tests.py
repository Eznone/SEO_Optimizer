from django.test import TestCase
from .services import SitemapGenerator
import xml.etree.ElementTree as ET

class SitemapGeneratorTest(TestCase):
    def test_generate_xml(self):
        urls = ["https://example.com/page1", "https://example.com/page2"]
        generator = SitemapGenerator(urls, changefreq="daily", priority=0.8)
        xml_content = generator.generate_xml()
        
        # Check if the output is bytes and starts with XML declaration
        self.assertIsInstance(xml_content, bytes)
        self.assertTrue(xml_content.startswith(b"<?xml"))
        
        # Parse XML to verify content
        root = ET.fromstring(xml_content)
        self.assertEqual(root.tag, "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
        
        url_elements = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        self.assertEqual(len(url_elements), 2)
        
        for i, url_el in enumerate(url_elements):
            loc = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            changefreq = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq").text
            priority = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority").text
            
            self.assertEqual(loc, urls[i])
            self.assertEqual(changefreq, "daily")
            self.assertEqual(priority, "0.8")
