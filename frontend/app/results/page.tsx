"use client";

import { useEffect, useState } from "react";
import { type TemplateResponse } from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<TemplateResponse | null>(null);
  const [activeTab, setActiveTab] = useState<
    "template" | "validation" | "audit"
  >("template");

  useEffect(() => {
    // Load result from session storage
    const storedResult = sessionStorage.getItem("latestQueryResult");
    if (storedResult) {
      setResult(JSON.parse(storedResult));
    } else {
      // No result found, redirect to query page
      router.push("/query");
    }
  }, [router]);

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading results...</p>
        </div>
      </div>
    );
  }

  const populatedFields = result.fields.filter(
    (f) => f.value !== null && f.value !== undefined,
  );
  const errorCount = result.validation_issues.filter(
    (v) => v.severity === "error",
  ).length;
  const warningCount = result.validation_issues.filter(
    (v) => v.severity === "warning",
  ).length;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="text-2xl font-bold text-slate-900 hover:text-blue-600 transition-colors"
          >
            COREP Assistant
          </Link>
          <Link
            href="/query"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            New Query
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-6 py-8 w-full">
        {/* Summary Cards */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            {result.template_name} Results
          </h1>
          <p className="text-slate-600">Query ID: {result.query_id}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="text-sm text-slate-600 mb-1">Fields Populated</div>
            <div className="text-3xl font-bold text-blue-600">
              {populatedFields.length}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="text-sm text-slate-600 mb-1">Validation Errors</div>
            <div
              className={`text-3xl font-bold ${errorCount > 0 ? "text-red-600" : "text-green-600"}`}
            >
              {errorCount}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="text-sm text-slate-600 mb-1">Warnings</div>
            <div
              className={`text-3xl font-bold ${warningCount > 0 ? "text-yellow-600" : "text-green-600"}`}
            >
              {warningCount}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="text-sm text-slate-600 mb-1">Audit Entries</div>
            <div className="text-3xl font-bold text-purple-600">
              {result.audit_log.length}
            </div>
          </div>
        </div>

        {/* Missing Data & Assumptions */}
        {(result.missing_data.length > 0 || result.assumptions.length > 0) && (
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            {result.missing_data.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                <h3 className="font-semibold text-yellow-900 mb-3">
                  ⚠️ Missing Data
                </h3>
                <ul className="space-y-2">
                  {result.missing_data.map((item, idx) => (
                    <li key={idx} className="text-sm text-yellow-800">
                      • {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.assumptions.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                <h3 className="font-semibold text-blue-900 mb-3">
                  💡 Assumptions Made
                </h3>
                <ul className="space-y-2">
                  {result.assumptions.map((item, idx) => (
                    <li key={idx} className="text-sm text-blue-800">
                      • {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="border-b border-slate-200 flex">
            {[
              { id: "template" as const, label: "Template", icon: "📊" },
              {
                id: "validation" as const,
                label: "Validation",
                icon: "✓",
                badge: errorCount + warningCount,
              },
              {
                id: "audit" as const,
                label: "Audit Log",
                icon: "📝",
                badge: result.audit_log.length,
              },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 px-6 py-4 font-semibold transition-colors relative ${
                  activeTab === tab.id
                    ? "text-blue-600 bg-blue-50 border-b-2 border-blue-600"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <span className="flex items-center justify-center gap-2">
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                  {tab.badge !== undefined && tab.badge > 0 && (
                    <span className="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">
                      {tab.badge}
                    </span>
                  )}
                </span>
              </button>
            ))}
          </div>

          <div className="p-6">
            {activeTab === "template" && (
              <div>
                <h2 className="text-xl font-bold text-slate-900 mb-4">
                  Populated Template Fields
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-slate-100">
                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-700 border">
                          Field Code
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-700 border">
                          Label
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-semibold text-slate-700 border">
                          Value
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-slate-700 border">
                          Confidence
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {populatedFields.map((field) => (
                        <tr
                          key={field.field_code}
                          className="hover:bg-slate-50"
                        >
                          <td className="px-4 py-3 text-sm font-mono text-slate-900 border">
                            {field.field_code}
                          </td>
                          <td className="px-4 py-3 text-sm text-slate-700 border">
                            {field.label}
                          </td>
                          <td className="px-4 py-3 text-sm font-semibold text-right text-slate-900 border">
                            {typeof field.value === "number"
                              ? field.value.toLocaleString()
                              : field.value}
                          </td>
                          <td className="px-4 py-3 text-center border">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium ${
                                field.confidence === "high"
                                  ? "bg-green-100 text-green-700"
                                  : field.confidence === "medium"
                                    ? "bg-yellow-100 text-yellow-700"
                                    : field.confidence === "low"
                                      ? "bg-orange-100 text-orange-700"
                                      : "bg-gray-100 text-gray-700"
                              }`}
                            >
                              {field.confidence}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {populatedFields.length === 0 && (
                  <p className="text-center text-slate-500 py-8">
                    No fields were populated
                  </p>
                )}
              </div>
            )}

            {activeTab === "validation" && (
              <div>
                <h2 className="text-xl font-bold text-slate-900 mb-4">
                  Validation Report
                </h2>
                {result.validation_issues.length > 0 ? (
                  <div className="space-y-3">
                    {result.validation_issues.map((issue, idx) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-lg border ${
                          issue.severity === "error"
                            ? "bg-red-50 border-red-200"
                            : issue.severity === "warning"
                              ? "bg-yellow-50 border-yellow-200"
                              : "bg-blue-50 border-blue-200"
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-lg">
                            {issue.severity === "error"
                              ? "❌"
                              : issue.severity === "warning"
                                ? "⚠️"
                                : "ℹ️"}
                          </span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono text-sm font-semibold">
                                {issue.field_code}
                              </span>
                              <span
                                className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                                  issue.severity === "error"
                                    ? "bg-red-200 text-red-800"
                                    : issue.severity === "warning"
                                      ? "bg-yellow-200 text-yellow-800"
                                      : "bg-blue-200 text-blue-800"
                                }`}
                              >
                                {issue.severity.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-sm text-slate-700 mb-2">
                              {issue.message}
                            </p>
                            {issue.suggestion && (
                              <p className="text-sm text-slate-600 italic">
                                💡 {issue.suggestion}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✅</div>
                    <h3 className="text-xl font-semibold text-green-700 mb-2">
                      All Checks Passed!
                    </h3>
                    <p className="text-slate-600">No validation issues found</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === "audit" && (
              <div>
                <h2 className="text-xl font-bold text-slate-900 mb-4">
                  Audit Trail
                </h2>
                <div className="space-y-4">
                  {result.audit_log.map((entry, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-50 p-5 rounded-lg border border-slate-200"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <span className="font-mono text-sm font-bold text-slate-900">
                            {entry.field_code}
                          </span>
                          <span className="mx-2 text-slate-400">→</span>
                          <span className="font-semibold text-blue-600">
                            {typeof entry.value === "number"
                              ? entry.value.toLocaleString()
                              : entry.value}
                          </span>
                        </div>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            entry.confidence === "high"
                              ? "bg-green-100 text-green-700"
                              : entry.confidence === "medium"
                                ? "bg-yellow-100 text-yellow-700"
                                : entry.confidence === "low"
                                  ? "bg-orange-100 text-orange-700"
                                  : "bg-gray-100 text-gray-700"
                          }`}
                        >
                          {entry.confidence}
                        </span>
                      </div>

                      <div className="bg-white p-4 rounded border border-slate-200 mb-3">
                        <h4 className="text-xs font-semibold text-slate-700 mb-2">
                          REASONING
                        </h4>
                        <p className="text-sm text-slate-700">
                          {entry.reasoning}
                        </p>
                      </div>

                      {entry.source_rules.length > 0 && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-700 mb-2">
                            SOURCE RULES
                          </h4>
                          <div className="space-y-2">
                            {entry.source_rules.map((rule, rIdx) => (
                              <div
                                key={rIdx}
                                className="bg-white p-3 rounded border border-slate-200"
                              >
                                <div className="font-mono text-xs font-semibold text-blue-600 mb-1">
                                  {rule.rule_id}
                                </div>
                                <p className="text-xs text-slate-600">
                                  {rule.rule_text}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="mt-3 text-xs text-slate-500">
                        Retrieved:{" "}
                        {new Date(entry.retrieved_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
                {result.audit_log.length === 0 && (
                  <p className="text-center text-slate-500 py-8">
                    No audit entries available
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Download Button */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={() => {
              const dataStr = JSON.stringify(result, null, 2);
              const dataBlob = new Blob([dataStr], {
                type: "application/json",
              });
              const url = URL.createObjectURL(dataBlob);
              const link = document.createElement("a");
              link.href = url;
              link.download = `corep_result_${result.query_id}.json`;
              link.click();
            }}
            className="px-6 py-3 bg-slate-100 text-slate-700 rounded-lg font-medium hover:bg-slate-200 transition-colors border border-slate-300"
          >
            📥 Download Full Report (JSON)
          </button>
        </div>
      </main>
    </div>
  );
}
