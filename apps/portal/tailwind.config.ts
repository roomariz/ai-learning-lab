import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#05070c",
          900: "#0b1020",
          800: "#111827",
        },
        signal: {
          amber: "#f59e0b",
          blue: "#38bdf8",
          green: "#34d399",
          red: "#fb7185",
        },
      },
      boxShadow: {
        soft: "0 24px 80px rgba(0, 0, 0, 0.22)",
      },
    },
  },
  plugins: [],
};

export default config;
