import { BOT_COLORS, timeAgo } from "../lib/format";

export default function SignalFeed({ data }) {
  if (!data) return null;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900">
      <div className="flex items-center justify-between border-b border-gray-800 px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
          Signal Feed
        </h2>
        <span className="text-xs text-gray-500">{data.count} signals</span>
      </div>

      {data.signals.length === 0 ? (
        <p className="px-4 py-8 text-center text-sm text-gray-600">
          No recent signals
        </p>
      ) : (
        <div className="max-h-96 overflow-y-auto divide-y divide-gray-800/50">
          {data.signals.map((sig) => {
            const c = BOT_COLORS[sig.bot_id] || {};
            const isLong = sig.direction === "LONG";
            return (
              <div
                key={`${sig.bot_id}-${sig.id}`}
                className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-800/30"
              >
                {/* Direction arrow */}
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-sm font-bold ${
                    isLong
                      ? "bg-emerald-500/20 text-emerald-400"
                      : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {isLong ? "\u2191" : "\u2193"}
                </span>

                {/* Symbol + bot */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{sig.symbol}</span>
                    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] ${c.bg} ${c.text}`}>
                      <span className={`h-1 w-1 rounded-full ${c.dot}`} />
                      {sig.bot_name}
                    </span>
                  </div>
                  {sig.source && (
                    <p className="text-xs text-gray-500">{sig.source}</p>
                  )}
                </div>

                {/* Score */}
                {sig.score != null && (
                  <span className="shrink-0 text-xs tabular-nums text-gray-400">
                    {(sig.score * 100).toFixed(0)}%
                  </span>
                )}

                {/* Time */}
                <span className="shrink-0 text-xs text-gray-600">
                  {timeAgo(sig.created_at)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
