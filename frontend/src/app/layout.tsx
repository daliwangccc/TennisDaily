import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "TennisDaily - 每日网球资讯",
  description: "每日网球新闻、比赛数据、ATP/WTA排名追踪",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 min-h-screen flex flex-col">
        {/* Navbar */}
        <nav className="bg-tennis-green text-white shadow-md">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="text-xl font-bold tracking-wide">
              TennisDaily
            </Link>
            <div className="flex gap-6 text-sm">
              <Link href="/" className="hover:text-tennis-ball transition">
                首页
              </Link>
              <Link href="/news" className="hover:text-tennis-ball transition">
                新闻
              </Link>
              <Link
                href="/matches"
                className="hover:text-tennis-ball transition"
              >
                比赛
              </Link>
              <Link
                href="/rankings"
                className="hover:text-tennis-ball transition"
              >
                排名
              </Link>
            </div>
          </div>
        </nav>

        {/* Content */}
        <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-tennis-dark text-gray-300 text-center py-4 text-sm">
          &copy; 2026 TennisDaily &mdash; 每日网球资讯
        </footer>
      </body>
    </html>
  );
}
