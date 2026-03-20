"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { apiFetch, ENDPOINTS, getBackendUrl } from "@/lib/api";

type CrawlJob = {
  id: string;
  target_url: string;
  status: string;
  total_pages_crawled: number;
  llms_txt_url: string | null;
  created_at: string;
};

export default function LlmsTxtDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [job, setJob] = useState<CrawlJob | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<CrawlJob>(`${ENDPOINTS.START_CRAWL.replace('/start', '/status')}/${id}`)
      .then(setJob)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="animate-pulse space-y-4 pt-10 text-center text-gray-400">Loading LLMS.txt details...</div>;
  if (!job) return <div className="text-center pt-10 text-red-600 font-bold">Audit not found.</div>;

  return (
    <div className="space-y-8 pb-20">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <nav className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Link href="/dashboard/llms-txt" className="hover:text-indigo-600">LLMS.txt</Link>
            <span>/</span>
            <span className="font-medium text-gray-900 truncate max-w-[200px]">{job.target_url}</span>
          </nav>
          <h1 className="text-3xl font-extrabold text-gray-900">LLMS.txt Results</h1>
        </div>
        
        {job.llms_txt_url && (
          <a 
            href={getBackendUrl(job.llms_txt_url)} 
            target="_blank"
            className="inline-flex items-center justify-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-indigo-700 transition-all shadow-md"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            Download llms.txt
          </a>
        )}
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Status</p>
          <p className="text-2xl font-black text-gray-900 flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${job.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
            {job.status}
          </p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Pages Crawled</p>
          <p className="text-2xl font-black text-gray-900">{job.total_pages_crawled}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Generated On</p>
          <p className="text-xl font-black text-gray-900">{new Date(job.created_at).toLocaleDateString()}</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">LLMS.txt Preview</h2>
          <span className="text-sm text-gray-500">AI-optimized documentation</span>
        </div>
        <div className="p-10 text-center">
          {job.llms_txt_url ? (
            <div className="space-y-4">
              <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto text-2xl">
                🤖
              </div>
              <p className="text-gray-600 font-medium">Your LLMS.txt file is ready and hosted at:</p>
              <code className="block bg-gray-50 p-4 rounded-xl border border-gray-200 text-indigo-600 break-all select-all">
                {getBackendUrl(job.llms_txt_url)}
              </code>
              <p className="text-xs text-gray-400">This file helps AI models understand your site structure and key content.</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="w-16 h-16 bg-yellow-50 text-yellow-600 rounded-full flex items-center justify-center mx-auto text-2xl">
                ⏳
              </div>
              <p className="text-gray-600 font-medium">LLMS.txt is being generated or was not created.</p>
              <p className="text-sm text-gray-400">This feature might require a successful deep crawl completion.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
