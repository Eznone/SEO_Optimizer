"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { apiFetch, ENDPOINTS } from "@/lib/api";

type CrawlJob = {
  id: string;
  target_url: string;
  status: string;
  total_pages_crawled: number;
  created_at: string;
};

export default function EeatDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [job, setJob] = useState<CrawlJob | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<CrawlJob>(`${ENDPOINTS.START_CRAWL.replace('/start', '/status')}/${id}`)
      .then(setJob)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="animate-pulse space-y-4 pt-10 text-center text-gray-400">Loading E-E-A-T analysis...</div>;
  if (!job) return <div className="text-center pt-10 text-red-600 font-bold">Audit not found.</div>;

  return (
    <div className="space-y-8 pb-20">
      <header>
        <nav className="flex items-center gap-2 text-sm text-gray-500 mb-2">
          <Link href="/dashboard/eeat" className="hover:text-indigo-600">E-E-A-T</Link>
          <span>/</span>
          <span className="font-medium text-gray-900 truncate max-w-[200px]">{job.target_url}</span>
        </nav>
        <h1 className="text-3xl font-extrabold text-gray-900">E-E-A-T Analysis Results</h1>
      </header>

      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm text-center py-20">
        <div className="w-20 h-20 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl">
          🛡️
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Detailed Scoring Coming Soon</h2>
        <p className="text-gray-500 max-w-lg mx-auto mb-8">
          We are currently processing the E-E-A-T signals for <strong>{job.target_url}</strong>. 
          The scoring model uses AI to evaluate expertise, authoritativeness, and trust factors.
        </p>
        <div className="flex justify-center gap-4 text-sm font-bold">
          <div className="px-4 py-2 bg-gray-100 rounded-lg">Pages: {job.total_pages_crawled}</div>
          <div className="px-4 py-2 bg-gray-100 rounded-lg">Status: {job.status}</div>
        </div>
      </div>
    </div>
  );
}
