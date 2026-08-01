import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function Forecast() {
  const { data: revenue } = useQuery({
    queryKey: ["forecast-revenue"],
    queryFn: () => api.get("/api/v1/forecast/revenue?days=30").then((r) => r.data),
  });

  const { data: brief } = useQuery({
    queryKey: ["daily-brief"],
    queryFn: () => api.get("/api/v1/forecast/daily-brief").then((r) => r.data),
  });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Forecast & Daily Brief</h1>

      {/* Daily Brief */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Daily Brief</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            (brief?.health_score ?? 100) >= 80
              ? "bg-green-100 text-green-800"
              : (brief?.health_score ?? 100) >= 50
              ? "bg-amber-100 text-amber-800"
              : "bg-red-100 text-red-800"
          }`}>
            Health: {brief?.health_score ?? "—"}/100
          </span>
        </div>
        <p className="text-xl font-medium mb-3">{brief?.headline ?? "No brief available yet"}</p>
        <p className="text-gray-600">{brief?.forecast_summary}</p>
        {brief?.action_items?.length > 0 && (
          <div className="mt-4">
            <h3 className="font-medium text-sm text-gray-500 mb-2">Action Items:</h3>
            <ul className="list-disc list-inside space-y-1">
              {brief.action_items.map((item: string, i: number) => (
                <li key={i} className="text-sm">{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Revenue Forecast */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Revenue Forecast (30 days)</h2>
        <p className="text-gray-600 mb-2">Trend: {revenue?.trend ?? "—"}</p>
        <p className="text-gray-600">{revenue?.summary}</p>
        {revenue?.data_points?.length > 0 ? (
          <div className="mt-4 overflow-x-auto">
            <div className="text-sm text-gray-500">
              {revenue.data_points.length} forecast points generated
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-400 mt-2">
            Generate demo data to see revenue forecasts.
          </p>
        )}
      </div>
    </div>
  );
}
