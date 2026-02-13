export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Active Agents" value="12" trend="+2" />
        <StatCard title="Running Tasks" value="8" trend="+3" />
        <StatCard title="Completed Today" value="24" trend="+15" />
        <StatCard title="Avg Response" value="1.2s" trend="-0.3s" />
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  trend,
}: {
  title: string;
  value: string;
  trend: string;
}) {
  return (
    <div
      className="p-4 rounded-lg"
      style={{
        background: "var(--surface-1)",
        border: "1px solid var(--line-1)",
      }}
    >
      <p className="text-sm text-muted">{title}</p>
      <div className="flex items-end justify-between mt-2">
        <span className="text-2xl font-bold">{value}</span>
        <span
          className="text-sm"
          style={{
            color: trend.startsWith("+")
              ? "var(--brand-tertiary)"
              : trend.startsWith("-")
              ? "var(--brand-secondary)"
              : "var(--muted)",
          }}
        >
          {trend}
        </span>
      </div>
    </div>
  );
}
