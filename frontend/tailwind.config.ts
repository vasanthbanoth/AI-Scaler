import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          green: "#22c55e",
          purple: "#7c3aed",
          pink: "#db2777",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 4px 24px rgba(15, 23, 42, 0.08)",
        float: "0 20px 60px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
