"use client";

import { Bell, Search, User } from "lucide-react";

export function Header() {
  return (
    <header
      className="h-16 flex items-center justify-between px-6"
      style={{
        background: "var(--surface-1)",
        borderBottom: "1px solid var(--line-1)",
      }}
    >
      <div className="flex items-center gap-4">
        <div
          className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{ background: "var(--surface-2)" }}
        >
          <Search className="w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent border-none outline-none text-sm w-48"
          />
          <kbd
            className="px-2 py-0.5 text-xs rounded"
            style={{ background: "var(--surface-3)" }}
          >
            Ctrl+K
          </kbd>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button
          className="p-2 rounded-lg hover:bg-surface-2 transition-colors relative"
        >
          <Bell className="w-5 h-5 text-muted" />
          <span
            className="absolute top-1 right-1 w-2 h-2 rounded-full"
            style={{ background: "var(--brand-primary)" }}
          />
        </button>
        <button className="flex items-center gap-2 p-2 rounded-lg hover:bg-surface-2 transition-colors">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background: "var(--brand-secondary)" }}
          >
            <User className="w-4 h-4" />
          </div>
        </button>
      </div>
    </header>
  );
}
