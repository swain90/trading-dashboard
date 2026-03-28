import { BOT_COLORS, formatMoney, pnlColor, pnlBg, formatTime } from "../lib/format";

function StatsBar({ stats }) {
  return (
    <div className="grid grid-cols-2 gap-2 px-4 py-3 sm:grid-cols-4 border-b border-gray-800">
      <div>
        <p className="text-[10px] uppercase text-gray-500">Trades</p>
        <p className="text-sm font-semibold">{stats.total_trades}</p>
      </div>
      <div>
        <p className="text-[10px] uppercase text-gray-500">Win Rate</p>
        <p className={`text-sm font-semibold ${stats.win_rate >= 50 ? "text-emerald-400" : "text-red-400"}`}>
          {stats.win_rate}%
        </p>
      </div>
      <div>
        <p className="text-[10px] uppercase text-gray-500">Total P&L</p>
        <p className={`text-sm font-semibold ${pnlColor(stats.total_pnl)}`}>
          {formatMoney(stats.total_pnl)}
        </p>
      </div>
      <div>
        <p className="text-[10px] uppercase text-gray-500">Avg P&L</p>
        <p className={`text-sm font-semibold ${pnlColor(stats.avg_pnl)}`}>
          {formatMoney(stats.avg_pnl)}
        </p>
      </div>
    </div>
  );
}

export default function TradeHistory({ data }) {
  if (!data) return null;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900">
      <div className="flex items-center justify-between border-b border-gray-800 px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
          Trade History (7d)
        </h2>
        <span className="text-xs text-gray-500">{data.count} trades</span>
      </div>

      <StatsBar stats={data.stats} />

      {data.trades.length === 0 ? (
        <p className="px-4 py-8 text-center text-sm text-gray-600">
          No closed trades in this period
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-xs uppercase tracking-wider text-gray-500">
                <th className="px-4 py-2">Symbol</th>
                <th className="px-4 py-2">Bot</th>
                <th className="px-4 py-2">Side</th>
                <th className="px-4 py-2 text-right">Entry</th>
                <th className="px-4 py-2 text-right">Exit</th>
                <th className="px-4 py-2 text-right">P&L</th>
                <th className="px-4 py-2 text-right">Closed</th>
              </tr>
            </thead>
            <tbody>
              {data.trades.map((t) => {
                const c = BOT_COLORS[t.bot_id] || {};
                return (
                  <tr
                    key={`${t.bot_id}-${t.id}`}
                    className={`border-b border-gray-800/50 hover:bg-gray-800/30 ${pnlBg(t.pnl)}`}
                  >
                    <td className="px-4 py-2 font-medium">{t.symbol}</td>
                    <td className="px-4 py-2">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${c.bg} ${c.text}`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
                        {t.bot_name}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-xs font-medium">
                      {t.side}
                    </td>
                    <td className="px-4 py-2 text-right tabular-nums">{formatMoney(t.entry_price)}</td>
                    <td className="px-4 py-2 text-right tabular-nums">{formatMoney(t.exit_price)}</td>
                    <td className={`px-4 py-2 text-right font-semibold tabular-nums ${pnlColor(t.pnl)}`}>
                      {formatMoney(t.pnl)}
                    </td>
                    <td className="px-4 py-2 text-right text-xs text-gray-500">
                      {formatTime(t.closed_at)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
