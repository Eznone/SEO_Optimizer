import ToolJobList from "@/components/ToolJobList";

export default function SitemapPage() {
  return (
    <ToolJobList 
      toolName="Sitemap Generator" 
      toolPath="sitemap"
      description="Automatically crawl your site and generate a search-engine-optimized XML sitemap with correct priorities and change frequencies."
    />
  );
}
