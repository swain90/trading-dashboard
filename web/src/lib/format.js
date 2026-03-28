export const BOT_COLORS = {
  whale_watcher: { bg: "bg-bot-ww/20", text: "text-bot-ww", dot: "bg-bot-ww" },
  commodity_hunter: { bg: "bg-bot-ch/20", text: "text-bot-ch", dot: "bg-bot-ch" },
  crypto: { bg: "bg-bot-crypto/20", text: "text-bot-crypto", dot: "bg-bot-crypto" },
};

export function botBadge(botId, botName) {
  const c = BOT_COLORS[botId] || { bg: "bg-gray-700", text: "text-gray-300" };
  return `inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${c.bg} ${c.text}`;
}

export function pnlColor(value) {
  if (value > 0) return "text-emerald-400";
  if (value < 0) return "text-red-400";
  return "text-gray-400";
}

export function pnlBg(value) {
  if (value > 0) return "bg-emerald-500/10";
  if (value < 0) return "bg-red-500/10";
  return "";
}

export function formatMoney(value, decimals = 2) {
  if (value == null) return "--";
  const prefix = value >= 0 ? "" : "-";
  return `${prefix}$${Math.abs(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

export function formatPct(value) {
  if (value == null) return "--";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatTime(isoString) {
  if (!isoString) return "--";
  return new Date(isoString).toLocaleString();
}

export function timeAgo(isoString) {
  if (!isoString) return "never";
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}
