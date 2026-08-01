import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function Audit() {
  const { data, isLoading } = useQuery({
    queryKey: ["audit-events"],
    queryFn: () => api.get("/api/v1/audit/events?limit=50").then((r) => r.data),
    refetchInterval: 15000,
  });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Audit Trail</h1>
      <p className="text-gray-600">
        Complete activity log — every agent action, user decision, and system event.
      </p>

      <div className="bg-white rounded-lg shadow">
        {isLoading ? (
          <div className="p-6 text-gray-500">Loading audit trail...</div>
        ) : data?.events?.length > 0 ? (
          <div className="divide-y">
            {data.events.map((event: any, i: number) => (
              <div key={i} className="p-4 flex items-start gap-4">
                <div className={`w-2 h-2 mt-2 rounded-full ${
                  event.actor === "agent" ? "bg-blue-500" :
                  event.actor?.startsWith("user") ? "bg-green-500" : "bg-gray-400"
                }`} />
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <p className="font-medium text-sm">{event.description}</p>
                    <span className="text-xs text-gray-400">
                      {new Date(event.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex gap-2 mt-1">
                    <span className="text-xs px-2 py-0.5 bg-gray-100 rounded">
                      {event.event_type}
                    </span>
                    <span className="text-xs text-gray-500">{event.actor}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center text-gray-500">
            No audit events yet. Activity will appear here as the agent operates.
          </div>
        )}
      </div>
    </div>
  );
}
