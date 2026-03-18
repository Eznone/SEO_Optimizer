import logging
from apps.crawler.models import CrawlJob, CrawledPage, AuditIssue
import json

logger = logging.getLogger(__name__)

class SchemaValidator:
    def __init__(self, job: CrawlJob):
        self.job = job

    def validate(self):
        pages = CrawledPage.objects.filter(job=self.job, status_code=200)
        for page in pages:
            if not page.json_ld_payload:
                continue
            
            for schema in page.json_ld_payload:
                self._check_schema_node(page, schema)
                self._check_schema_drift(page, schema)

    def _check_schema_drift(self, page, node):
        """Simple check to see if schema data matches visible content."""
        schema_name = node.get('name')
        if schema_name and page.title:
            # Very loose check: if name is not in title and title is not in name
            # (only if name is substantial)
            if len(schema_name) > 10 and schema_name.lower() not in page.title.lower() and page.title.lower() not in schema_name.lower():
                 AuditIssue.objects.create(
                    job=self.job,
                    page=page,
                    issue_type='schema_drift',
                    severity='low',
                    description=f"Potential drift: Schema name '{schema_name}' does not match page title '{page.title}'."
                )

    def _check_schema_node(self, page, node):
        node_type = node.get('@type')
        if not node_type:
            return

        # Handle list of types
        if isinstance(node_type, list):
            types = node_type
        else:
            types = [node_type]

        for t in types:
            if t == 'LocalBusiness' or (isinstance(t, str) and 'LocalBusiness' in t):
                self._validate_local_business(page, node)
            elif t == 'Organization':
                self._validate_organization(page, node)

        # Recursively check nested nodes (like 'publisher', 'author', 'address', etc.)
        for key, value in node.items():
            if isinstance(value, dict):
                self._check_schema_node(page, value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._check_schema_node(page, item)

    def _validate_local_business(self, page, node):
        geo = node.get('geo')
        if not geo:
            AuditIssue.objects.create(
                job=self.job,
                page=page,
                issue_type='schema_missing_coordinates',
                severity='medium',
                description="LocalBusiness schema is missing 'geo' (latitude/longitude) coordinates."
            )
        else:
            lat = geo.get('latitude')
            lon = geo.get('longitude')
            if not lat or not lon:
                AuditIssue.objects.create(
                    job=self.job,
                    page=page,
                    issue_type='schema_missing_coordinates',
                    severity='medium',
                    description="LocalBusiness 'geo' coordinates are incomplete (missing latitude or longitude)."
                )

    def _validate_organization(self, page, node):
        same_as = node.get('sameAs')
        if not same_as:
            AuditIssue.objects.create(
                job=self.job,
                page=page,
                issue_type='schema_missing_sameas',
                severity='low',
                description="Organization schema is missing 'sameAs' links to authoritative profiles (e.g., LinkedIn, Wikipedia)."
            )

def process_schema_validation(job_id: str):
    """Orchestrates schema validation for a crawl job."""
    try:
        job = CrawlJob.objects.get(id=job_id)
        validator = SchemaValidator(job)
        validator.validate()
        logger.info(f"Schema validation completed for job {job_id}")
    except CrawlJob.DoesNotExist:
        logger.error(f"CrawlJob {job_id} not found for schema validation")
    except Exception as e:
        logger.error(f"Error validating schema for job {job_id}: {e}")
