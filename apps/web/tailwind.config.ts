import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17201d",
        muted: "#66736f",
        line: "#d8dfdc",
        panel: "#ffffff",
        canvas: "#f4f7f5",
        teal: "#147d72",
        coral: "#c4493d",
        amber: "#b07918"
      },
      boxShadow: {
        panel: "0 14px 40px rgba(23, 32, 29, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;

