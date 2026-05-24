import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentSec Arena",
  description: "Local-only AI cyber range defense evaluation dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

