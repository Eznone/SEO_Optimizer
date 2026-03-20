"use client";

import { useEffect, useState, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { apiFetch, ENDPOINTS } from "@/lib/api";

type UserProfile = {
  username: string;
  email: string;
  has_groq_key: boolean;
};

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check authentication
    apiFetch<UserProfile>(ENDPOINTS.ME)
      .then((data) => {
        setProfile(data);
      })
      .catch((err) => {
        console.error("Auth error:", err);
        router.push("/");
      })
      .finally(() => setLoading(false));
  }, [router]);

  const handleLogout = async () => {
    try {
      await apiFetch(ENDPOINTS.LOGOUT, { method: "POST" });
      router.push("/");
    } catch (err) {
      console.error("Logout error:", err);
      router.push("/");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600 font-medium">Verifying session...</p>
        </div>
      </div>
    );
  }

  const navItems = [
    { name: "Overview", href: "/dashboard", icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
    )},
    { name: "SEO Audit", href: "/dashboard/seo-audit", icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
    )},
    { name: "E-E-A-T Analysis", href: "/dashboard/eeat", icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
    )},
    { name: "LLMS.txt", href: "/dashboard/llms-txt", icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
    )},
    { name: "Sitemap", href: "/dashboard/sitemap", icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" /></svg>
    )},
    { name: "Settings", href: "/dashboard/settings", icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
    )},
  ];

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden font-sans">
      {/* Sidebar - Collapsible on Hover */}
      <aside className="group w-20 hover:w-64 bg-white border-r border-gray-200 flex flex-col hidden md:flex transition-all duration-300 ease-in-out z-20">
        <div className="p-6 border-b border-gray-200 overflow-hidden whitespace-nowrap">
          <Link href="/dashboard" className="text-xl font-bold text-indigo-600 flex items-center gap-3">
            <svg className="w-8 h-8 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" /><path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" /></svg>
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 font-bold">Analyzer</span>
          </Link>
        </div>
        <nav className="flex-1 p-4 space-y-2 overflow-hidden">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                title={item.name}
                className={`flex items-center gap-4 px-3 py-3 rounded-xl font-medium transition-all duration-200 whitespace-nowrap ${
                  isActive
                    ? "bg-indigo-50 text-indigo-600 shadow-sm"
                    : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
                }`}
              >
                <div className={`flex-shrink-0 ${isActive ? "text-indigo-600" : "text-gray-400 group-hover:text-gray-600"}`}>
                  {item.icon}
                </div>
                <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {item.name}
                </span>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-200 overflow-hidden">
          <div className="flex items-center gap-4 px-2 py-3 bg-gray-50 rounded-xl whitespace-nowrap">
            <div className="w-10 h-10 bg-indigo-100 text-indigo-600 rounded-xl flex-shrink-0 flex items-center justify-center font-bold text-lg">
              {profile?.username?.[0]?.toUpperCase() || profile?.email?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 overflow-hidden opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <p className="text-sm font-bold text-gray-900 truncate">{profile?.username || "User"}</p>
              <p className="text-xs text-gray-500 truncate">{profile?.email}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 z-10">
          <div className="md:hidden">
            <Link href="/dashboard" className="text-xl font-bold text-indigo-600">SEO Analyzer</Link>
          </div>
          <div className="hidden md:block">
            <h1 className="text-lg font-semibold text-gray-900">
              {navItems.find(item => item.href === pathname)?.name || "Dashboard"}
            </h1>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${profile?.has_groq_key ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
              <span className="text-xs text-gray-500 font-medium">
                {profile?.has_groq_key ? 'AI Analysis Enabled' : 'AI Analysis Disabled'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="text-sm font-medium text-gray-600 hover:text-red-600 transition-colors"
            >
              Sign out
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-10 bg-gray-50">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
