import { BOT_COLORS, formatMoney, formatPct, pnlColor } from "../lib/format";

function StatCard({ label, value, sub, className = "" }) {
  return (
    <div className={`rounded-xl border border-gray-800 bg-gray-900 p-4 ${className}`}>
      <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
      {sub && <p className="mt-0.5 text-sm">{sub}</p>}
    </div>
  );
}

function BotCard({ bot }) {
  const c = BOT_COLORS[bot.id] || {};
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${c.dot}`} />
          <span className={`text-sm font-medium ${c.text}`}>{bot.name}</span>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${
            bot.status === "running"
              ? "bg-emerald-500/20 text-emerald-400"
              : bot.status === "stopped"
              ? "bg-yellow-500/20 text-yellow-400"
              : "bg-red-500/20 text-red-400"
          }`}
        >
          {bot.status}
        </span>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs text-gray-500">Equity</p>
          <p className="text-sm font-semibold">{formatMoney(bot.equity)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Today P&L</p>
          <p className={`text-sm font-semibold ${pnlColor(bot.today_pnl)}`}>
            {formatMoney(bot.today_pnl)} ({formatPct(bot.today_pnl_pct)})
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Positions</p>
          <p className="text-sm font-semibold">{bot.open_positions}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Signals Today</p>
          <p className="text-sm font-semibold">{bot.signals_today}</p>
        </div>
      </div>
    </div>
  );
}

export default function OverviewCards({ data }) {
  if (!data) return null;
  const { combined, bots } = data;

  return (
    <div className="space-y-4">
      {/* Combined stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard
          label="Total Equity"
          value={formatMoney(combined.total_equity)}
        />
        <StatCard
          label="Today P&L"
          value={formatMoney(combined.today_pnl)}
          sub={
            <span className={pnlColor(combined.today_pnl)}>
              {formatPct(combined.today_pnl_pct)}
            </span>
          }
          className={combined.today_pnl >= 0 ? "border-emerald-900/50" : "border-red-900/50"}
        />
        <StatCard
          label="Open Positions"
          value={combined.open_positions}
        />
        <StatCard
          label="Signals Today"
          value={combined.signals_today}
        />
      </div>

      {/* Per-bot cards */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {bots.map((bot) => (
          <BotCard key={bot.id} bot={bot} />
        ))}
      </div>
    </div>
  );
}
