import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-4" style={{ color: "var(--brand-primary)" }}>
          MAIOS
        </h1>
        <p className="text-xl text-muted mb-8">
          Metamorphic AI Orchestration System
        </p>
        <Link
          href="/dashboard"
          className="px-6 py-3 rounded-lg font-medium transition-all duration-200"
          style={{
            background: "var(--brand-primary)",
            color: "var(--surface-1)",
          }}
        >
          Enter Dashboard
        </Link>
      </div>
    </main>
  );
}
