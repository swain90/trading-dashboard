/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bot: {
          ww: "#3b82f6",      // blue — Whale Watcher
          ch: "#f97316",      // orange — Commodity Hunter
          crypto: "#a855f7",  // purple — Crypto
          fm: "#ec4899",      // pink — Forecast Maker
          cc: "#14b8a6",      // teal — Currency Compass
        },
      },
    },
  },
  plugins: [],
};
