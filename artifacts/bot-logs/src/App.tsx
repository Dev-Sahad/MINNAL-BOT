import { useState, useEffect, useRef, useCallback } from "react";
import { Switch, Route, Router as WouterRouter } from "wouter";

const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

type Log = { timestamp: string; message: string; severity: string };
type Status = { status: string; deploymentId?: string; createdAt?: string; updatedAt?: string; project?: string; service?: string; error?: string };

const SEV_COLOR: Record<string, string> = {
  ERROR: "text-red-400",
  WARN: "text-yellow-400",
  WARNING: "text-yellow-400",
  INFO: "text-blue-300",
  DEBUG: "text-gray-400",
};

const STATUS_COLOR: Record<string, string> = {
  SUCCESS: "bg-green-500",
  DEPLOYING: "bg-yellow-500",
  FAILED: "bg-red-500",
  CRASHED: "bg-red-600",
  REMOVED: "bg-gray-500",
  UNKNOWN: "bg-gray-600",
};

function timeSince(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString("en-US", { hour12: false });
}

function LogLine({ log, filter }: { log: Log; filter: string }) {
  const cls = SEV_COLOR[log.severity?.toUpperCase()] ?? "text-gray-300";
  const msg = log.message ?? "";
  if (filter && !msg.toLowerCase().includes(filter.toLowerCase())) return null;

  const parts = filter
    ? msg.split(new RegExp(`(${filter})`, "gi"))
    : [msg];

  return (
    <div className="flex gap-3 py-0.5 font-mono text-xs hover:bg-white/5 rounded px-1 group">
      <span className="text-gray-600 shrink-0 w-20 pt-[1px]">{fmtTime(log.timestamp)}</span>
      <span className={`shrink-0 w-12 uppercase font-bold text-[10px] pt-[2px] ${cls}`}>{log.severity ?? "INFO"}</span>
      <span className="text-gray-200 break-all leading-relaxed">
        {parts.map((p, i) =>
          filter && p.toLowerCase() === filter.toLowerCase()
            ? <mark key={i} className="bg-yellow-400/30 text-yellow-200 rounded px-0.5">{p}</mark>
            : p
        )}
      </span>
    </div>
  );
}

function Dashboard() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [status, setStatus] = useState<Status | null>(null);
  const [filter, setFilter] = useState("");
  const [autoScroll, setAutoScroll] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastFetch, setLastFetch] = useState<Date | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchLogs = useCallback(async () => {
    try {
      const [logsRes, statusRes] = await Promise.all([
        fetch(`/api/railway/logs?limit=200`),
        fetch(`/api/railway/status`),
      ]);
      const logsData = await logsRes.json() as { logs?: Log[]; error?: string };
      const statusData = await statusRes.json() as Status;

      if (logsData.error) throw new Error(logsData.error);
      setLogs((logsData.logs ?? []).reverse());
      setStatus(statusData);
      setLastFetch(new Date());
      setError("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 8000);
    return () => clearInterval(interval);
  }, [fetchLogs]);

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, autoScroll]);

  const statusDot = status ? (STATUS_COLOR[status.status] ?? "bg-gray-600") : "bg-gray-600";
  const isOnline = status?.status === "SUCCESS";

  const filtered = filter ? logs.filter(l => (l.message ?? "").toLowerCase().includes(filter.toLowerCase())) : logs;

  const errorCount = logs.filter(l => l.severity?.toUpperCase() === "ERROR").length;
  const warnCount = logs.filter(l => ["WARN", "WARNING"].includes(l.severity?.toUpperCase())).length;

  return (
    <div className="min-h-screen bg-[#0d0d0d] text-gray-200 flex flex-col">
      {/* Header */}
      <header className="border-b border-white/10 px-4 py-3 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">⚡</span>
          <div>
            <h1 className="font-bold text-white leading-none">MINNAL Bot</h1>
            <p className="text-gray-500 text-xs">Railway · {status?.project ?? "..."}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 ml-2">
          <span className={`w-2.5 h-2.5 rounded-full ${statusDot} ${isOnline ? "animate-pulse" : ""}`} />
          <span className={`text-sm font-medium ${isOnline ? "text-green-400" : "text-red-400"}`}>
            {status?.status ?? "Loading..."}
          </span>
          {status?.updatedAt && (
            <span className="text-gray-600 text-xs">· {timeSince(status.updatedAt)}</span>
          )}
        </div>

        <div className="flex gap-4 ml-auto text-xs text-center">
          <div>
            <div className="text-white font-bold text-lg leading-none">{logs.length}</div>
            <div className="text-gray-500">Lines</div>
          </div>
          <div>
            <div className="text-red-400 font-bold text-lg leading-none">{errorCount}</div>
            <div className="text-gray-500">Errors</div>
          </div>
          <div>
            <div className="text-yellow-400 font-bold text-lg leading-none">{warnCount}</div>
            <div className="text-gray-500">Warns</div>
          </div>
        </div>
      </header>

      {/* Toolbar */}
      <div className="border-b border-white/10 px-4 py-2 flex gap-3 items-center">
        <div className="relative flex-1 max-w-sm">
          <input
            className="w-full bg-white/5 border border-white/10 rounded px-3 py-1.5 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500 pr-8"
            placeholder="Filter logs..."
            value={filter}
            onChange={e => setFilter(e.target.value)}
          />
          {filter && (
            <button onClick={() => setFilter("")} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white text-xs">✕</button>
          )}
        </div>

        <div className="flex gap-2 text-xs">
          {["ERROR", "WARN", "INFO"].map(sev => (
            <button
              key={sev}
              onClick={() => setFilter(sev)}
              className={`px-2 py-1 rounded border ${SEV_COLOR[sev]} border-white/10 hover:bg-white/10`}
            >
              {sev}
            </button>
          ))}
        </div>

        <label className="flex items-center gap-2 text-xs text-gray-400 ml-auto cursor-pointer select-none">
          <input type="checkbox" checked={autoScroll} onChange={e => setAutoScroll(e.target.checked)} className="accent-blue-500" />
          Auto-scroll
        </label>

        <button onClick={fetchLogs} className="text-xs text-gray-400 hover:text-white px-2 py-1 rounded hover:bg-white/10 border border-white/10">
          ↻ Refresh
        </button>

        {lastFetch && (
          <span className="text-xs text-gray-600">Updated {lastFetch.toLocaleTimeString()}</span>
        )}
      </div>

      {/* Logs */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        {loading && (
          <div className="text-gray-500 text-sm text-center py-12">Loading logs from Railway...</div>
        )}
        {error && (
          <div className="bg-red-900/30 border border-red-500/30 rounded p-3 text-red-300 text-sm mb-3">{error}</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <div className="text-gray-600 text-sm text-center py-12">No logs found{filter ? ` matching "${filter}"` : ""}</div>
        )}
        {filtered.map((log, i) => (
          <LogLine key={i} log={log} filter={filter} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 px-4 py-2 text-xs text-gray-600 flex gap-4">
        <span>Service: <span className="text-gray-400">{status?.service ?? "worker"}</span></span>
        {status?.deploymentId && <span>Deployment: <span className="text-gray-400 font-mono">{status.deploymentId.slice(0, 8)}</span></span>}
        <span className="ml-auto">Auto-refreshes every 8s</span>
      </div>
    </div>
  );
}

function App() {
  return (
    <WouterRouter base={BASE}>
      <Switch>
        <Route path="/" component={Dashboard} />
      </Switch>
    </WouterRouter>
  );
}

export default App;
