import { BOT_COLORS, timeAgo } from "../lib/format";

const STATUS_STYLES = {
  running: { dot: "bg-emerald-400 animate-pulse", text: "text-emerald-400", label: "Running" },
  stopped: { dot: "bg-yellow-400", text: "text-yellow-400", label: "Stopped" },
  unavailable: { dot: "bg-red-400", text: "text-red-400", label: "Unavailable" },
};

export default function BotStatus({ data }) {
  if (!data) return null;

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900">
      <div className="border-b border-gray-800 px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
          Bot Status
        </h2>
      </div>

      <div className="divide-y divide-gray-800/50">
        {data.bots.map((bot) => {
          const c = BOT_COLORS[bot.id] || {};
          const s = STATUS_STYLES[bot.status] || STATUS_STYLES.unavailable;
          return (
            <div key={bot.id} className="px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${c.dot}`} />
                  <span className={`text-sm font-medium ${c.text}`}>{bot.name}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className={`h-2 w-2 rounded-full ${s.dot}`} />
                  <span className={`text-xs ${s.text}`}>{s.label}</span>
                </div>
              </div>

              <div className="mt-2 grid grid-cols-3 gap-4 text-xs">
                <div>
                  <span className="text-gray-500">DB</span>
                  <span className={`ml-1 ${bot.db_connected ? "text-emerald-400" : "text-red-400"}`}>
                    {bot.db_connected ? "Connected" : "Disconnected"}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Last Signal</span>
                  <span className="ml-1 text-gray-300">{timeAgo(bot.last_signal)}</span>
                </div>
                <div>
                  <span className="text-gray-500">Today</span>
                  <span className="ml-1 text-gray-300">
                    {bot.trades_today} trades, {bot.open_positions} open
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
