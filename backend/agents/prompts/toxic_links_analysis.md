Analyze the following list of outgoing links from a website. 
Identify if any of these appear to be 'link farms', spammy directories, or high-risk 'bad neighborhoods' for SEO in 2026.

Links:
{links}

Return the result ONLY in JSON format:
{{
    "toxic_links": [
        {{"url": "toxic-url.com", "reason": "Known link farm", "severity": "high"}}
    ]
}}
If none are toxic, return an empty list for "toxic_links".
