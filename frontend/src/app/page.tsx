export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <header className="w-full py-6 px-8 bg-white shadow-sm flex justify-between items-center">
        <div className="text-2xl font-bold text-indigo-600 tracking-tight">
          SEO Analyzer
        </div>
        <nav className="flex space-x-4">
          <a
            href="/accounts/google/login/"
            className="text-gray-600 hover:text-indigo-600 font-medium px-3 py-2 rounded-md transition-colors"
          >
            Login
          </a>
          <a
            href="/accounts/google/login/"
            className="bg-indigo-600 text-white px-5 py-2 rounded-md font-medium hover:bg-indigo-700 transition-colors shadow-sm"
          >
            Get Started
          </a>
        </nav>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 text-center mt-12 md:mt-24">
        <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight max-w-4xl">
          Elevate Your Site&apos;s <span className="text-indigo-600">E-E-A-T</span> & Rankings
        </h1>
        <p className="mt-6 text-xl text-gray-500 max-w-2xl mx-auto">
          AI-powered SEO audits, conversational search readiness, schema validation, and comprehensive crawl analysis—all in one place.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/accounts/google/login/"
            className="w-full sm:w-auto flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg shadow-md transition-all"
          >
            Sign in with Google
          </a>
          <a
            href="/accounts/github/login/"
            className="w-full sm:w-auto flex items-center justify-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 md:py-4 md:text-lg shadow-sm transition-all"
          >
            Sign in with GitHub
          </a>
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full text-left pb-20">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mb-4 text-2xl font-bold">
              1
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Automated Crawling</h3>
            <p className="text-gray-500">
              Deep dive into your site structure to uncover broken links, missing metadata, and indexing issues effortlessly.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mb-4 text-2xl font-bold">
              2
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">AI-Driven Insights</h3>
            <p className="text-gray-500">
              Analyze your content for E-E-A-T readiness and generate llms.txt files optimized for next-gen search engines.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mb-4 text-2xl font-bold">
              3
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Schema Validation</h3>
            <p className="text-gray-500">
              Ensure your structured data exactly matches your content, avoiding drift and securing rich snippets.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
