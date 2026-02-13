"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FolderKanban,
  Users,
  Brain,
  Settings,
  Network,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/projects", label: "Projects", icon: FolderKanban },
  { href: "/dashboard/agents", label: "Agents", icon: Users },
  { href: "/dashboard/neural", label: "Neural View", icon: Network },
  { href: "/dashboard/memory", label: "Memory", icon: Brain },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="w-64 h-screen flex flex-col"
      style={{
        background: "var(--surface-1)",
        borderRight: "1px solid var(--line-1)",
      }}
    >
      <div className="p-4 border-b" style={{ borderColor: "var(--line-1)" }}>
        <h1
          className="text-xl font-bold"
          style={{ color: "var(--brand-primary)" }}
        >
          MAIOS
        </h1>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-200",
                    isActive
                      ? "bg-surface-2 text-[var(--brand-primary)]"
                      : "text-muted hover:text-fg hover:bg-surface-2"
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
