import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function Dashboard() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: () => api.get("/api/v1/dashboard/overview").then((r) => r.data),
    refetchInterval: 30000, // Refresh every 30s
  });

  if (isLoading) {
    return <div className="p-6">Loading dashboard...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">LedgerMind Dashboard</h1>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Revenue Today"
          value={`$${overview?.metrics?.revenue_today?.toLocaleString() ?? "0"}`}
        />
        <MetricCard
          title="Transactions"
          value={overview?.metrics?.transactions_today ?? 0}
        />
        <MetricCard
          title="Failure Rate"
          value={`${overview?.metrics?.failure_rate ?? 0}%`}
          alert={overview?.metrics?.failure_rate > 5}
        />
        <MetricCard
          title="Health Score"
          value={overview?.health_score ?? 100}
        />
      </div>

      {/* Agent Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Agent Activity</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Active Tasks</p>
            <p className="text-2xl font-bold">{overview?.agent?.active_tasks ?? 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Pending Approvals</p>
            <p className="text-2xl font-bold text-amber-600">
              {overview?.agent?.pending_approvals ?? 0}
            </p>
          </div>
        </div>
      </div>

      {/* Anomalies */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Detected Anomalies</h2>
        {overview?.anomalies?.length > 0 ? (
          <ul className="space-y-2">
            {overview.anomalies.map((anomaly: any, i: number) => (
              <li key={i} className="p-3 bg-red-50 rounded border border-red-200">
                {anomaly.description}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No anomalies detected. All systems normal.</p>
        )}
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  alert = false,
}: {
  title: string;
  value: string | number;
  alert?: boolean;
}) {
  return (
    <div className={`bg-white rounded-lg shadow p-4 ${alert ? "border-l-4 border-red-500" : ""}`}>
      <p className="text-sm text-gray-500">{title}</p>
      <p className={`text-2xl font-bold ${alert ? "text-red-600" : ""}`}>{value}</p>
    </div>
  );
}
