import { Link, useLocation } from "react-router-dom";
import { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
  user: any;
  onSignOut: (() => void) | undefined;
}

const navItems = [
  { path: "/", label: "Dashboard", icon: "📊" },
  { path: "/agent", label: "Agent", icon: "🤖" },
  { path: "/approvals", label: "Approvals", icon: "✅" },
  { path: "/payments", label: "Payments", icon: "💳" },
  { path: "/forecast", label: "Forecast", icon: "📈" },
  { path: "/audit", label: "Audit", icon: "📋" },
];

export function Layout({ children, user, onSignOut }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-blue-600">LedgerMind</h1>
          <p className="text-xs text-gray-500">AI Payment Operations</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition ${
                location.pathname === item.path
                  ? "bg-blue-50 text-blue-700 font-medium"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t">
          <p className="text-sm text-gray-600 truncate">{user?.username}</p>
          <button
            onClick={onSignOut}
            className="mt-2 text-sm text-red-600 hover:text-red-800"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
