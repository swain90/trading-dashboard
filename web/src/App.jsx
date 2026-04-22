import { api } from "./lib/api";
import { useApi } from "./hooks/useApi";
import OverviewCards from "./components/OverviewCards";
import PositionsTable from "./components/PositionsTable";
import SignalFeed from "./components/SignalFeed";
import TradeHistory from "./components/TradeHistory";
import BotStatus from "./components/BotStatus";

function ErrorBanner({ message }) {
  return (
    <div className="rounded-lg border border-red-900/50 bg-red-950/50 px-4 py-3 text-sm text-red-400">
      <span className="font-medium">Connection error:</span> {message}
    </div>
  );
}

function LastUpdated({ time }) {
  if (!time) return null;
  return (
    <span className="text-xs text-gray-600">
      Updated {time.toLocaleTimeString()}
    </span>
  );
}

export default function App() {
  const overview = useApi(() => api.overview());
  const positions = useApi(() => api.positions());
  const signals = useApi(() => api.signals(50));
  const trades = useApi(() => api.trades(7));
  const health = useApi(() => api.health());

  const loading = overview.loading && positions.loading;
  const error = overview.error || positions.error;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      {/* Header */}
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight sm:text-2xl">
            Trading Command Center
          </h1>
          <p className="text-sm text-gray-500">
            {overview.data?.bots?.length || 0} bots &middot; unified view
          </p>
        </div>
        <div className="flex items-center gap-3">
          <LastUpdated time={overview.lastUpdated} />
          <button
            onClick={() => {
              overview.refresh();
              positions.refresh();
              signals.refresh();
              trades.refresh();
              health.refresh();
            }}
            className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-1.5 text-xs font-medium text-gray-300 hover:bg-gray-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </header>

      {/* Error */}
      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      {/* Loading skeleton */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-32 animate-pulse rounded-xl border border-gray-800 bg-gray-900"
            />
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Overview */}
          <OverviewCards data={overview.data} />

          {/* Main grid: positions + signals side by side on desktop */}
          <div className="grid gap-6 lg:grid-cols-2">
            <PositionsTable data={positions.data} />
            <SignalFeed data={signals.data} />
          </div>

          {/* Trade history full width */}
          <TradeHistory data={trades.data} />

          {/* Bot status */}
          <BotStatus data={health.data} />
        </div>
      )}

      {/* Footer */}
      <footer className="mt-8 border-t border-gray-800 pt-4 text-center text-xs text-gray-600">
        Trading Command Center &middot; Auto-refresh every 30s
      </footer>
    </div>
  );
}
