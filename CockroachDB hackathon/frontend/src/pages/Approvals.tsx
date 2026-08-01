import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";

export function Approvals() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["pending-approvals"],
    queryFn: () => api.get("/api/v1/approvals/pending").then((r) => r.data),
    refetchInterval: 10000,
  });

  const decideMutation = useMutation({
    mutationFn: ({ id, status, reason }: { id: string; status: string; reason?: string }) =>
      api.post(`/api/v1/approvals/${id}/decide`, { status, reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-approvals"] });
    },
  });

  if (isLoading) {
    return <div className="p-6">Loading approvals...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Pending Approvals</h1>
      <p className="text-gray-600">
        The agent recommends these actions. Review and approve or reject before execution.
      </p>

      {data?.approvals?.length > 0 ? (
        <div className="space-y-4">
          {data.approvals.map((approval: any) => (
            <div key={approval.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{approval.summary}</h3>
                  <p className="text-gray-600 mt-1">{approval.explanation}</p>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    approval.risk_level === "high"
                      ? "bg-red-100 text-red-800"
                      : approval.risk_level === "medium"
                      ? "bg-amber-100 text-amber-800"
                      : "bg-green-100 text-green-800"
                  }`}
                >
                  {approval.risk_level} risk
                </span>
              </div>

              <div className="mt-4 p-3 bg-gray-50 rounded">
                <p className="text-sm font-medium">Proposed Action:</p>
                <p className="text-sm text-gray-700">{approval.proposed_action}</p>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <p className="text-sm text-gray-500">
                  Confidence: {(approval.confidence * 100).toFixed(0)}%
                </p>
              </div>

              <div className="mt-4 flex gap-3">
                <button
                  onClick={() => decideMutation.mutate({ id: approval.id, status: "approved" })}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Approve
                </button>
                <button
                  onClick={() => decideMutation.mutate({ id: approval.id, status: "rejected" })}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
          No pending approvals. The agent will notify you when actions need your review.
        </div>
      )}
    </div>
  );
}
