"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, ENDPOINTS, getBackendUrl } from "@/lib/api";

type CrawlJob = {
  id: string;
  target_url: string;
  status: string;
  total_pages_crawled: number;
  sitemap_url: string | null;
  llms_txt_url: string | null;
  created_at: string;
};

interface ToolJobListProps {
  toolName: string;
  toolPath: string; // e.g. "sitemap", "eeat"
  description: string;
}

export default function ToolJobList({ toolName, toolPath, description }: ToolJobListProps) {
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    apiFetch<CrawlJob[]>(ENDPOINTS.JOBS)
      .then((data) => setJobs(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-extrabold text-gray-900 mb-2">{toolName}</h1>
        <p className="text-gray-500 max-w-2xl">{description}</p>
        <div className="mt-4 p-4 bg-indigo-50 border border-indigo-100 rounded-xl flex items-start gap-3">
          <svg className="w-5 h-5 text-indigo-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <p className="text-sm text-indigo-800 font-medium">
            <strong>Pro Tip:</strong> After reviewing your {toolName}, try running a different analysis to get a 360° view of your site's SEO health!
          </p>
        </div>
      </header>

      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-6">Select a Previous Audit</h2>
        
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-40 bg-gray-100 rounded-2xl border border-gray-200"></div>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-white p-12 rounded-2xl border border-gray-200 text-center shadow-sm">
            <div className="w-16 h-16 bg-gray-50 text-gray-300 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
              🔍
            </div>
            <p className="text-lg font-medium text-gray-600">No crawl jobs found.</p>
            <p className="text-sm text-gray-400 mt-1">
              Go to the <Link href="/dashboard" className="text-indigo-600 hover:underline">Dashboard</Link> to start your first analysis.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jobs.map((job) => (
              <div 
                key={job.id} 
                className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all h-full flex flex-col"
              >
                <div className="flex justify-between items-start mb-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    job.status === 'completed' ? 'bg-green-100 text-green-800' :
                    job.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {job.status}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(job.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-gray-900 truncate mb-2">
                  {job.target_url}
                </h3>
                <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                  <div className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                    {job.total_pages_crawled} pages
                  </div>
                </div>

                <div className="mt-auto space-y-3">
                  <div className="flex flex-wrap gap-2">
                    {job.sitemap_url && (
                      <a 
                        href={getBackendUrl(job.sitemap_url)} 
                        target="_blank" 
                        className="text-xs font-bold text-indigo-600 hover:underline px-2 py-1 bg-indigo-50 rounded"
                      >
                        XML Sitemap
                      </a>
                    )}
                    {job.llms_txt_url && (
                      <a 
                        href={getBackendUrl(job.llms_txt_url)} 
                        target="_blank" 
                        className="text-xs font-bold text-indigo-600 hover:underline px-2 py-1 bg-indigo-50 rounded"
                      >
                        LLMS.txt
                      </a>
                    )}
                  </div>
                  
                  <Link 
                    href={`/dashboard/${toolPath}/${job.id}`}
                    className="w-full inline-flex items-center justify-center px-4 py-2.5 bg-indigo-600 text-white text-sm font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-sm gap-2"
                  >
                    View Report 
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
