import { useState } from "react";
import { BOT_COLORS, formatMoney, pnlColor, formatTime } from "../lib/format";

const COLUMNS = [
  { key: "symbol", label: "Symbol" },
  { key: "bot_name", label: "Bot" },
  { key: "side", label: "Side" },
  { key: "size", label: "Size" },
  { key: "entry_price", label: "Entry" },
  { key: "current_price", label: "Current" },
  { key: "unrealized_pnl", label: "Unreal. P&L" },
  { key: "stop_loss", label: "SL" },
  { key: "take_profit", label: "TP" },
];

export default function PositionsTable({ data }) {
  const [sortKey, setSortKey] = useState("unrealized_pnl");
  const [sortAsc, setSortAsc] = useState(false);

  if (!data) return null;

  const positions = [...data.positions].sort((a, b) => {
    const av = a[sortKey] ?? 0;
    const bv = b[sortKey] ?? 0;
    return sortAsc ? av - bv : bv - av;
  });

  function toggleSort(key) {
    if (sortKey === key) setSortAsc(!sortAsc);
    else {
      setSortKey(key);
      setSortAsc(false);
    }
  }

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900">
      <div className="flex items-center justify-between border-b border-gray-800 px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
          Open Positions
        </h2>
        <span className="text-xs text-gray-500">{data.count} total</span>
      </div>

      {positions.length === 0 ? (
        <p className="px-4 py-8 text-center text-sm text-gray-600">
          No open positions
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-xs uppercase tracking-wider text-gray-500">
                {COLUMNS.map((col) => (
                  <th
                    key={col.key}
                    className="cursor-pointer px-4 py-2 hover:text-gray-300"
                    onClick={() => toggleSort(col.key)}
                  >
                    {col.label}
                    {sortKey === col.key && (sortAsc ? " \u25B2" : " \u25BC")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {positions.map((p) => {
                const c = BOT_COLORS[p.bot_id] || {};
                return (
                  <tr
                    key={`${p.bot_id}-${p.id}`}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30"
                  >
                    <td className="px-4 py-2 font-medium">{p.symbol}</td>
                    <td className="px-4 py-2">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${c.bg} ${c.text}`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
                        {p.bot_name}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded ${
                          p.side === "LONG"
                            ? "bg-emerald-500/20 text-emerald-400"
                            : "bg-red-500/20 text-red-400"
                        }`}
                      >
                        {p.side}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right tabular-nums">{p.size}</td>
                    <td className="px-4 py-2 text-right tabular-nums">{formatMoney(p.entry_price)}</td>
                    <td className="px-4 py-2 text-right tabular-nums">{formatMoney(p.current_price)}</td>
                    <td className={`px-4 py-2 text-right font-medium tabular-nums ${pnlColor(p.unrealized_pnl)}`}>
                      {formatMoney(p.unrealized_pnl)}
                    </td>
                    <td className="px-4 py-2 text-right tabular-nums text-gray-500">{formatMoney(p.stop_loss)}</td>
                    <td className="px-4 py-2 text-right tabular-nums text-gray-500">{formatMoney(p.take_profit)}</td>
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
