import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function Payments() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ["payment-summary"],
    queryFn: () => api.get("/api/v1/payments/summary?period=7d").then((r) => r.data),
  });

  const { data: failures } = useQuery({
    queryKey: ["payment-failures"],
    queryFn: () => api.get("/api/v1/payments/failures?limit=20").then((r) => r.data),
  });

  if (isLoading) {
    return <div className="p-6">Loading payments...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Payment Operations</h1>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Total Transactions (7d)</p>
          <p className="text-2xl font-bold">{summary?.total_transactions ?? 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Revenue (7d)</p>
          <p className="text-2xl font-bold">${summary?.total_revenue?.toLocaleString() ?? "0"}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Failure Rate</p>
          <p className="text-2xl font-bold">{summary?.failure_rate ?? 0}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-500">Avg Transaction</p>
          <p className="text-2xl font-bold">${summary?.avg_transaction_value ?? 0}</p>
        </div>
      </div>

      {/* Recent Failures */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Failures</h2>
        {failures?.failures?.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="pb-2">Time</th>
                <th className="pb-2">Amount</th>
                <th className="pb-2">Customer</th>
                <th className="pb-2">Reason</th>
              </tr>
            </thead>
            <tbody>
              {failures.failures.map((f: any, i: number) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="py-2">{new Date(f.created_at).toLocaleString()}</td>
                  <td className="py-2">${f.amount}</td>
                  <td className="py-2">{f.customer_email ?? "N/A"}</td>
                  <td className="py-2 text-red-600">{f.failure_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-gray-500">No recent failures. Looking good!</p>
        )}
      </div>
    </div>
  );
}
