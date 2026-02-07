import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-slate-900">
            LLM-Assisted COREP Reporting Assistant
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            AI-powered regulatory reporting for PRA COREP templates
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-6 py-12 w-full">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
            Prototype v0.1.0
          </div>

          <h2 className="text-5xl font-bold text-slate-900 mb-6">
            Simplify COREP Reporting
            <br />
            with <span className="text-blue-600">AI Intelligence</span>
          </h2>

          <p className="text-xl text-slate-600 max-w-3xl mx-auto mb-8">
            Transform natural language scenarios into accurate COREP template
            submissions. Get instant validation, audit trails, and regulatory
            compliance guidance.
          </p>

          <div className="flex gap-4 justify-center">
            <Link
              href="/query"
              className="px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
            >
              Start Query →
            </Link>
            <a
              href="http://localhost:8000/api/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-white text-slate-700 border-2 border-slate-200 rounded-lg font-semibold hover:border-slate-300 transition-colors"
            >
              API Documentation
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Natural Language Input
            </h3>
            <p className="text-slate-600">
              Describe your reporting scenario in plain English. Our AI
              interprets complex regulatory requirements automatically.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Intelligent Validation
            </h3>
            <p className="text-slate-600">
              Automated validation against PRA rules, business logic checks, and
              cross-field consistency verification.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Complete Audit Trail
            </h3>
            <p className="text-slate-600">
              Every populated field comes with full justification, source rule
              references, and confidence scores.
            </p>
          </div>
        </div>

        {/* Supported Templates */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
          <h3 className="text-2xl font-bold text-slate-900 mb-6">
            Supported COREP Templates
          </h3>

          <div className="space-y-4">
            <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg">
              <div className="flex-shrink-0 w-16 h-16 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold text-lg">
                CA1
              </div>
              <div className="flex-1">
                <h4 className="text-lg font-semibold text-slate-900">
                  Own Funds
                </h4>
                <p className="text-slate-600 text-sm mt-1">
                  Complete breakdown of Common Equity Tier 1, Additional Tier 1,
                  and Tier 2 capital components with regulatory adjustments.
                </p>
                <div className="flex gap-2 mt-3">
                  <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                    ✓ Available
                  </span>
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                    47 rows × 2 columns
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg opacity-50">
              <div className="flex-shrink-0 w-16 h-16 bg-slate-400 text-white rounded-lg flex items-center justify-center font-bold text-lg">
                CA3
              </div>
              <div className="flex-1">
                <h4 className="text-lg font-semibold text-slate-900">
                  Capital Requirements
                </h4>
                <p className="text-slate-600 text-sm mt-1">
                  Risk-weighted assets and capital requirements breakdown.
                </p>
                <div className="flex gap-2 mt-3">
                  <span className="px-3 py-1 bg-slate-300 text-slate-700 rounded-full text-xs font-medium">
                    Coming Soon
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sample Scenarios */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-slate-900 mb-6 text-center">
            Try These Sample Scenarios
          </h3>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
              <h4 className="font-semibold text-slate-900 mb-3">
                Simple Capital Structure
              </h4>
              <p className="text-sm text-slate-700 italic">
                "Our bank has CET1 capital of £500M, AT1 instruments of £100M,
                and Tier 2 capital of £200M. We have £50M in intangible assets
                and £30M in deferred tax assets. What should we report in CA1?"
              </p>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border border-green-200">
              <h4 className="font-semibold text-slate-900 mb-3">
                Complex Deductions
              </h4>
              <p className="text-sm text-slate-700 italic">
                "We have ordinary shares worth £300M, retained earnings of
                £150M, and other reserves of £50M. Our intangible assets total
                £40M, and we hold £20M of our own CET1 instruments. Calculate
                our CET1 capital."
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-sm text-slate-600">
          <p>LLM-Assisted COREP Reporting Assistant - Prototype © 2026</p>
          <p className="mt-1">Powered by Google Gemini 2.0 Flash</p>
        </div>
      </footer>
    </div>
  );
}
