from django.test import TestCase
from .services import SitemapGenerator, SiteAnalyzer
from .models import SitemapJob, Page, Link, AuditIssue, Recommendation
import xml.etree.ElementTree as ET

class SitemapGeneratorTest(TestCase):
    def test_generate_xml(self):
        job = SitemapJob.objects.create(target_url="https://example.com")
        page1 = Page.objects.create(job=job, url="https://example.com/page1", status_code=200, priority=1.0)
        page2 = Page.objects.create(job=job, url="https://example.com/page2", status_code=200, priority=0.8)

        generator = SitemapGenerator([page1, page2], changefreq="daily")
        xml_content = generator.generate_xml()
        
        # Check if the output is bytes and starts with XML declaration
        self.assertIsInstance(xml_content, bytes)
        self.assertTrue(xml_content.startswith(b"<?xml"))
        
        # Parse XML to verify content
        root = ET.fromstring(xml_content)
        self.assertEqual(root.tag, "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
        
        url_elements = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        self.assertEqual(len(url_elements), 2)
        
        expected_data = [
            ("https://example.com/page1", "daily", "1.0"),
            ("https://example.com/page2", "daily", "0.8")
        ]
        
        for i, url_el in enumerate(url_elements):
            loc = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            changefreq = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq").text
            priority = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority").text
            
            self.assertEqual(loc, expected_data[i][0])
            self.assertEqual(changefreq, expected_data[i][1])
            self.assertEqual(priority, expected_data[i][2])

class SiteAnalyzerTest(TestCase):
    def setUp(self):
        self.job = SitemapJob.objects.create(target_url="https://example.com")

    def test_orphan_page_detection(self):
        root_page = Page.objects.create(job=self.job, url="https://example.com", status_code=200, depth=0)
        orphan_page = Page.objects.create(job=self.job, url="https://example.com/orphan", status_code=200, depth=1)
        
        analyzer = SiteAnalyzer(self.job)
        analyzer.analyze()
        
        issues = AuditIssue.objects.filter(job=self.job, issue_type='orphan')
        self.assertEqual(issues.count(), 1)
        self.assertEqual(issues.first().page, orphan_page)

    def test_broken_link_detection(self):
        broken_page = Page.objects.create(job=self.job, url="https://example.com/broken", status_code=404, depth=1)
        
        analyzer = SiteAnalyzer(self.job)
        analyzer.analyze()
        
        issues = AuditIssue.objects.filter(job=self.job, issue_type='broken_link')
        self.assertEqual(issues.count(), 1)
        self.assertEqual(issues.first().page, broken_page)

    def test_duplicate_content_detection(self):
        page1 = Page.objects.create(job=self.job, url="https://example.com/1", status_code=200, depth=1, content_hash='abc')
        page2 = Page.objects.create(job=self.job, url="https://example.com/2", status_code=200, depth=1, content_hash='abc')
        
        analyzer = SiteAnalyzer(self.job)
        analyzer.analyze()
        
        issues = AuditIssue.objects.filter(job=self.job, issue_type='duplicate_content')
        self.assertEqual(issues.count(), 2)

    def test_recommendation_generation(self):
        # Create an orphan page issue scenario
        Page.objects.create(job=self.job, url="https://example.com/orphan", status_code=200, depth=1)
        
        analyzer = SiteAnalyzer(self.job)
        analyzer.analyze()
        
        recs = Recommendation.objects.filter(job=self.job, action_required__icontains="orphan pages")
        self.assertEqual(recs.count(), 1)

    def test_calculate_priorities(self):
        root_page = Page.objects.create(job=self.job, url="https://example.com", status_code=200, depth=0)
        page1 = Page.objects.create(job=self.job, url="https://example.com/p1", status_code=200, depth=1)
        page2 = Page.objects.create(job=self.job, url="https://example.com/p2", status_code=200, depth=2)
        
        # Link p1 and p2 to p1 (boosting p1's popularity)
        Link.objects.create(job=self.job, source_page=root_page, target_url="https://example.com/p1")
        Link.objects.create(job=self.job, source_page=page2, target_url="https://example.com/p1")
        
        analyzer = SiteAnalyzer(self.job)
        analyzer.calculate_priorities()
        
        root_page.refresh_from_db()
        page1.refresh_from_db()
        page2.refresh_from_db()
        
        # Root (depth 0, 0 links) -> Base 1.0 - 0 + 0 = 1.0
        self.assertEqual(root_page.priority, 1.0)
        # P1 (depth 1, 2 links) -> Base 1.0 - 0.2 + 0.2 = 1.0 (Popularity boost offsets depth decay)
        self.assertEqual(page1.priority, 1.0)
        # P2 (depth 2, 0 links) -> Base 1.0 - 0.4 + 0 = 0.6
        self.assertEqual(page2.priority, 0.6)
