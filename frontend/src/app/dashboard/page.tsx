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

type UserProfile = {
  username: string;
  email: string;
  has_groq_key: boolean;
};

export default function Dashboard() {
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [targetUrl, setTargetUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showWarningModal, setShowWarningModal] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await apiFetch<UserProfile>(ENDPOINTS.ME);
      setProfile(data);
    } catch (err) {
      console.error("Profile fetch error:", err);
    }
  };

  const fetchJobs = async () => {
    if (!loading) setRefreshing(true);
    try {
      const data = await apiFetch<CrawlJob[]>(ENDPOINTS.JOBS);
      setJobs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleLaunchClick = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl) return;

    if (profile && !profile.has_groq_key) {
      setShowWarningModal(true);
    } else {
      executeCrawl();
    }
  };

  const executeCrawl = async () => {
    setShowWarningModal(false);
    setCrawling(true);
    try {
      await apiFetch(ENDPOINTS.START_CRAWL, {
        method: "POST",
        body: JSON.stringify({ target_url: targetUrl, target_keywords: [] }),
      });

      setTargetUrl("");
      // Re-fetch jobs after a short delay
      setTimeout(fetchJobs, 2000);
    } catch (err) {
      console.error("Crawl error:", err);
    } finally {
      setCrawling(false);
    }
  };

  return (
    <div className="space-y-10">
      {/* Warning Modal */}
      {showWarningModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-200 max-w-md w-full p-8 animate-in fade-in zoom-in duration-200">
            <div className="w-16 h-16 bg-yellow-50 text-yellow-600 rounded-full flex items-center justify-center mb-6 text-2xl">
              ⚠️
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Missing Groq API Key</h3>
            <p className="text-gray-500 mb-8 leading-relaxed">
              You haven't set up your Groq API key yet. While the crawler will still work, 
              you won't get the full benefit of <span className="font-bold text-gray-900">AI-powered E-E-A-T analysis</span> and advanced SEO insights.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => setShowWarningModal(false)}
                className="flex-1 px-6 py-3 border border-gray-200 rounded-xl font-bold text-gray-600 hover:bg-gray-50 transition-all"
              >
                Cancel
              </button>
              <button
                onClick={executeCrawl}
                className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg"
              >
                Launch Anyway
              </button>
            </div>
            <p className="mt-6 text-center">
              <Link href="/dashboard/settings" className="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors underline underline-offset-4">
                Go to settings to add your key
              </Link>
            </p>
          </div>
        </div>
      )}

      <section>
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">New Analysis</h2>
          <p className="text-gray-500 mb-6">Enter a URL to start a comprehensive SEO and E-E-A-T audit.</p>
          <form onSubmit={handleLaunchClick} className="flex flex-col sm:flex-row gap-4">
            <input
              type="url"
              placeholder="https://example.com"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              required
              className="flex-1 px-5 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-gray-900 bg-gray-50 focus:bg-white"
            />
            <button
              type="submit"
              disabled={crawling}
              className="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2"
            >
              {crawling ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  Starting...
                </>
              ) : "Launch Crawler"}
            </button>
          </form>
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Recent Audits</h2>
            <p className="text-xs text-gray-500 mt-1">Audit complete? Experiment with our specialized tools in the sidebar!</p>
          </div>
          <button 
            onClick={fetchJobs}
            disabled={refreshing}
            className="text-sm font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1 bg-indigo-50 px-3 py-1.5 rounded-lg transition-colors"
          >
            <svg className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {loading && jobs.length === 0 ? (
          <div className="bg-white p-12 rounded-2xl border border-gray-200 text-center">
            <div className="inline-block animate-pulse text-indigo-600 mb-2">Loading your jobs...</div>
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-gray-500 bg-white p-12 rounded-2xl border border-gray-200 text-center shadow-sm">
            <div className="w-16 h-16 bg-gray-50 text-gray-300 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            </div>
            <p className="text-lg font-medium text-gray-600">No crawl jobs found.</p>
            <p className="text-sm text-gray-400 mt-1">Start your first analysis by entering a URL above!</p>
          </div>
        ) : (
          <div className="bg-white shadow-sm border border-gray-200 rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-left">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-8 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Target URL</th>
                    <th className="px-8 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-8 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-center">Pages</th>
                    <th className="px-8 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-8 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {jobs.map((job) => (
                    <tr key={job.id} className="hover:bg-gray-50 transition-colors group">
                      <td className="px-8 py-5 whitespace-nowrap">
                        <div className="text-sm font-bold text-gray-900">{job.target_url}</div>
                      </td>
                      <td className="px-8 py-5 whitespace-nowrap">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${
                          job.status === 'completed' ? 'bg-green-100 text-green-800' :
                          job.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full mr-2 ${
                            job.status === 'completed' ? 'bg-green-500' :
                            job.status === 'failed' ? 'bg-red-500' :
                            'bg-yellow-500'
                          }`}></span>
                          {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-8 py-5 whitespace-nowrap text-sm text-gray-500 text-center font-medium">
                        {job.total_pages_crawled}
                      </td>
                      <td className="px-8 py-5 whitespace-nowrap text-sm text-gray-500">
                        {new Date(job.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                      </td>
                      <td className="px-8 py-5 whitespace-nowrap text-right space-x-3">
                        {job.sitemap_url && (
                          <a 
                            href={getBackendUrl(job.sitemap_url)} 
                            target="_blank" 
                            className="text-xs font-bold text-indigo-600 hover:underline"
                          >
                            XML Sitemap
                          </a>
                        )}
                        <Link 
                          href={`/dashboard/seo-audit/${job.id}`}
                          className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-lg hover:bg-indigo-700 transition-all shadow-sm"
                        >
                          View Report
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

