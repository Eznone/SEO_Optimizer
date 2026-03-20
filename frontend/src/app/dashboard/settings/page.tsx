"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUpdateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    try {
      await apiFetch("/api/users/update-key", {
        method: "POST",
        body: JSON.stringify({ groq_key: apiKey }),
      });
      setStatus({ type: 'success', message: "API key updated successfully!" });
      setApiKey("");
    } catch (err: any) {
      setStatus({ type: 'error', message: err.message || "Failed to update API key." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">User Settings</h2>
        
        <div className="space-y-8">
          <section>
            <h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center gap-2">
              <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
              AI Analysis Configuration
            </h3>
            <p className="text-gray-500 text-sm mb-6">
              To enable AI-powered E-E-A-T analysis, provide your own **Groq API Key**. 
              Your key is stored securely with field-level encryption.
            </p>

            <form onSubmit={handleUpdateKey} className="space-y-4">
              <div>
                <label htmlFor="apiKey" className="block text-sm font-bold text-gray-700 mb-2">
                  Groq API Key
                </label>
                <input
                  id="apiKey"
                  type="password"
                  placeholder="gsk_..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-gray-900 bg-gray-50"
                  required
                />
              </div>
              
              {status && (
                <div className={`p-4 rounded-xl text-sm font-medium ${
                  status.type === 'success' ? 'bg-green-50 text-green-800 border border-green-100' : 'bg-red-50 text-red-800 border border-red-100'
                }`}>
                  {status.message}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-md"
              >
                {loading ? "Saving..." : "Update API Key"}
              </button>
            </form>
          </section>

          <hr className="border-gray-100" />

          <section>
            <h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center gap-2 text-red-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-4v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              Account Management
            </h3>
            <p className="text-gray-500 text-sm mb-4">
              Permanently delete your account and all associated crawl data.
            </p>
            <button className="text-sm font-bold text-red-600 hover:text-red-800 transition-colors">
              Delete Account
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}
