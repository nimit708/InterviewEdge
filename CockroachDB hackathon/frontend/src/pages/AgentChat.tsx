import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";

interface Message {
  role: "user" | "agent";
  content: string;
  requires_approval?: boolean;
}

export function AgentChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);

  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      api.post("/api/v1/agent/chat", { message, conversation_id: conversationId }),
    onSuccess: (response) => {
      const data = response.data;
      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: data.response, requires_approval: data.requires_approval },
      ]);
    },
  });

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    chatMutation.mutate(input);
    setInput("");
  };

  const quickActions = [
    { label: "Investigate failure spike", task: "investigate_failure_spike" },
    { label: "Create recovery list", task: "create_recovery_list" },
    { label: "Follow up inactive customers", task: "follow_up_inactive" },
    { label: "Monitor anomaly (24h)", task: "monitor_anomaly" },
    { label: "Suggest campaign", task: "prepare_campaign" },
    { label: "Schedule performance check", task: "schedule_performance_check" },
  ];

  return (
    <div className="p-6 flex flex-col h-full">
      <h1 className="text-2xl font-bold mb-4">LedgerMind Agent</h1>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-2 mb-4">
        {quickActions.map((action) => (
          <button
            key={action.task}
            onClick={() => {
              setMessages((prev) => [...prev, { role: "user", content: action.label }]);
              chatMutation.mutate(action.label);
            }}
            className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm hover:bg-blue-100 transition"
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-4 rounded-lg max-w-[80%] ${
              msg.role === "user"
                ? "bg-blue-100 ml-auto"
                : "bg-gray-100"
            }`}
          >
            <p className="text-sm font-medium mb-1">
              {msg.role === "user" ? "You" : "LedgerMind Agent"}
            </p>
            <p>{msg.content}</p>
            {msg.requires_approval && (
              <div className="mt-2 p-2 bg-amber-50 border border-amber-200 rounded">
                <p className="text-sm text-amber-700">⚠️ This action requires your approval</p>
                <div className="flex gap-2 mt-2">
                  <button className="px-3 py-1 bg-green-600 text-white rounded text-sm">
                    Approve
                  </button>
                  <button className="px-3 py-1 bg-red-600 text-white rounded text-sm">
                    Reject
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask the agent about your payment operations..."
          className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          onClick={handleSend}
          disabled={chatMutation.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
