"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { queryAPI, type QueryRequest, type TemplateResponse } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function QueryPage() {
  const router = useRouter();
  const [question, setQuestion] = useState("");
  const [templateId, setTemplateId] = useState("CA1");

  const mutation = useMutation({
    mutationFn: (request: QueryRequest) => queryAPI.processQuery(request),
    onSuccess: (data: TemplateResponse) => {
      // Store result in session storage for results page
      sessionStorage.setItem("latestQueryResult", JSON.stringify(data));
      router.push("/results");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim() || question.length < 10) {
      alert("Please provide a detailed scenario (at least 10 characters)");
      return;
    }

    mutation.mutate({
      question: question.trim(),
      template_id: templateId,
    });
  };

  const sampleScenarios = [
    {
      icon: "🏦",
      title: "Complete Capital Structure",
      text: "Our bank has CET1 capital of £500M, AT1 instruments of £100M, and Tier 2 capital of £200M. We have £50M in intangible assets and £30M in deferred tax assets. What should we report in CA1?",
    },
    {
      icon: "📊",
      title: "CET1 Calculation",
      text: "We have ordinary shares worth £300M, retained earnings of £150M, and other reserves of £50M. Our intangible assets total £40M, and we hold £20M of our own CET1 instruments. Calculate our CET1 capital.",
    },
  ];

  const handleSampleClick = (scenarioText: string) => {
    setQuestion(scenarioText);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="text-2xl font-bold text-slate-900 hover:text-blue-600 transition-colors"
          >
            COREP Assistant
          </Link>
          <a
            href="http://localhost:8000/api/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-slate-600 hover:text-slate-900"
          >
            API Docs →
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl mx-auto px-6 py-12 w-full">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">
            Submit COREP Query
          </h1>
          <p className="text-lg text-slate-600">
            Describe your regulatory reporting scenario in natural language, and
            our AI will populate the COREP template with full justifications.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Template Selection */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <label
              htmlFor="template"
              className="block text-sm font-semibold text-slate-900 mb-2"
            >
              Target COREP Template
            </label>
            <select
              id="template"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={mutation.isPending}
            >
              <option value="CA1">CA1 - Own Funds</option>
              <option value="CA3" disabled>
                CA3 - Capital Requirements (Coming Soon)
              </option>
            </select>
          </div>

          {/* Question Input */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <label
              htmlFor="question"
              className="block text-sm font-semibold text-slate-900 mb-2"
            >
              Reporting Scenario <span className="text-red-500">*</span>
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Describe your bank's capital position, including CET1, AT1, T2 components, deductions, and any relevant details..."
              className="w-full px-4 py-3 border-2 border-slate-300 rounded-xl 
                       bg-white text-slate-900 placeholder-slate-500
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                       min-h-[200px] font-mono text-sm shadow-sm hover:shadow-md transition-shadow"
              disabled={mutation.isPending}
              required
            />
            <p className="mt-2 text-sm text-slate-500">
              {question.length} characters · Minimum 10 characters required
            </p>
          </div>

          {/* Sample Scenarios */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-3">
              💡 Try a sample scenario
            </h3>
            <div className="grid gap-4 md:grid-cols-2">
              {sampleScenarios.map((scenario, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSampleClick(scenario.text)}
                  className="group p-5 rounded-xl border-2 border-slate-700 bg-slate-900/50 hover:bg-slate-800/50
                                         text-left transition-all duration-300 hover:border-blue-500
                                         hover:shadow-lg hover:shadow-blue-500/20 backdrop-blur-sm
                                         transform hover:scale-[1.02]"
                  disabled={mutation.isPending}
                >
                  <h4 className="font-bold text-white mb-2 flex items-center gap-2">
                    <span className="text-2xl">{scenario.icon}</span>
                    {scenario.title}
                  </h4>
                  <p className="text-sm transition-colors line-clamp-2">
                    {scenario.text}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {mutation.isError && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h3 className="font-semibold text-red-900 mb-2">
                ⚠️ Error Processing Query
              </h3>
              <p className="text-red-700 text-sm">
                {mutation.error instanceof Error
                  ? mutation.error.message
                  : "An unexpected error occurred. Please try again."}
              </p>
              <p className="text-red-600 text-xs mt-2">
                Tip: Make sure the backend server is running at
                http://localhost:8000
              </p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={
                mutation.isPending || !question.trim() || question.length < 10
              }
              className="flex-1 px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors shadow-lg hover:shadow-xl"
            >
              {mutation.isPending ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Processing Query...
                </span>
              ) : (
                "Generate COREP Report →"
              )}
            </button>

            <Link
              href="/"
              className="px-8 py-4 bg-white text-slate-700 border-2 border-slate-200 rounded-lg font-semibold hover:border-slate-300 transition-colors"
            >
              Cancel
            </Link>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-12 bg-slate-100 rounded-xl p-6 border border-slate-200">
          <h3 className="font-semibold text-slate-900 mb-3">
            ℹ️ What happens next?
          </h3>
          <ol className="space-y-2 text-sm text-slate-700">
            <li className="flex gap-2">
              <span className="font-bold text-blue-600">1.</span>
              <span>
                Your scenario is analyzed against PRA Rulebook sections
                retrieved from the knowledge base
              </span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold text-blue-600">2.</span>
              <span>
                Gemini AI interprets regulatory requirements and populates CA1
                template fields
              </span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold text-blue-600">3.</span>
              <span>
                Automated validation checks ensure calculation accuracy and
                compliance
              </span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold text-blue-600">4.</span>
              <span>
                Complete audit trail shows which rules justified each field
                value
              </span>
            </li>
          </ol>
        </div>
      </main>
    </div>
  );
}
