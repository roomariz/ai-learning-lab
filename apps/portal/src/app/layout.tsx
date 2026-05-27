import type { Metadata } from "next";
import type React from "react";
import { Inter } from "next/font/google";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://ai-learning-lab.roomariz.dev"),
  title: {
    default: "AI Learning Lab",
    template: "%s | AI Learning Lab",
  },
  description:
    "A runtime-aware AI engineering portfolio covering RAG, evaluation, tool calling, MCP, local agents, and deployable web demos.",
  openGraph: {
    title: "AI Learning Lab",
    description:
      "A public showcase for AI learning projects with Vercel apps, Streamlit dashboards, and local-only agent labs.",
    url: "https://ai-learning-lab.roomariz.dev",
    siteName: "AI Learning Lab",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-zinc-950"
        >
          Skip to content
        </a>
        <SiteHeader />
        <main id="main">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
