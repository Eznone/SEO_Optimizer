"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type UserProfile = {
  username: string;
  email: string;
  has_groq_key: boolean;
};

type CrawlJob = {
  id: string;
  target_url: string;
  status: string;
  total_pages_crawled: number;
  created_at: string;
};

export default function Dashboard() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [targetUrl, setTargetUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check authentication
    fetch("/api/users/me")
      .then((res) => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((data) => {
        setProfile(data);
        fetchJobs();
      })
      .catch(() => {
        router.push("/");
      })
      .finally(() => setLoading(false));
  }, [router]);

  const fetchJobs = () => {
    fetch("/api/crawler/jobs")
      .then((res) => res.json())
      .then((data) => setJobs(data))
      .catch(console.error);
  };

  const startCrawl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl) return;

    setCrawling(true);
    try {
      const res = await fetch("/api/crawler/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ target_url: targetUrl, target_keywords: [] }),
      });

      if (res.ok) {
        setTargetUrl("");
        // Re-fetch jobs or wait a moment
        setTimeout(fetchJobs, 1000);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setCrawling(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <header className="w-full py-4 px-8 bg-white shadow-sm flex justify-between items-center">
        <div className="text-xl font-bold text-indigo-600">SEO Analyzer Dashboard</div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">Welcome, {profile?.username || profile?.email}</span>
          <a
            href="/accounts/logout/"
            className="text-sm text-red-600 hover:text-red-800 font-medium"
          >
            Logout
          </a>
        </div>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Initialize a New Crawl</h2>
          <form onSubmit={startCrawl} className="flex gap-4">
            <input
              type="url"
              placeholder="https://example.com"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              required
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-shadow text-gray-900"
            />
            <button
              type="submit"
              disabled={crawling}
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {crawling ? "Starting..." : "Start Crawl"}
            </button>
          </form>
        </div>

        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Recent Jobs</h2>
          {jobs.length === 0 ? (
            <div className="text-gray-500 bg-white p-8 rounded-xl border border-gray-200 text-center">
              No crawl jobs found. Start one above!
            </div>
          ) : (
            <div className="bg-white shadow-sm border border-gray-200 rounded-xl overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200 text-left">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Target URL</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Pages Crawled</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {jobs.map((job) => (
                    <tr key={job.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {job.target_url}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          job.status === 'completed' ? 'bg-green-100 text-green-800' :
                          job.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {job.total_pages_crawled}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(job.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
