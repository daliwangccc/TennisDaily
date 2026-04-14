import { apiFetch } from "@/lib/api";

interface Article {
  id: number;
  title: string;
  summary: string | null;
  category: string | null;
  published_at: string | null;
}

interface Match {
  id: number;
  player1_name: string | null;
  player2_name: string | null;
  score: string | null;
  round: string | null;
  match_date: string | null;
  status: string;
}

interface Ranking {
  rank: number;
  player_name: string | null;
  points: number;
}

async function getNews() {
  try {
    const data = await apiFetch<{ items: Article[] }>("/api/news?page_size=5");
    return data.items;
  } catch {
    return [];
  }
}

async function getMatches() {
  try {
    const data = await apiFetch<{ items: Match[] }>(
      "/api/matches?page_size=5"
    );
    return data.items;
  } catch {
    return [];
  }
}

async function getRankings(tour: string) {
  try {
    const data = await apiFetch<{ items: Ranking[] }>(
      `/api/rankings?tour=${tour}&type=singles&limit=5`
    );
    return data.items;
  } catch {
    return [];
  }
}

export default async function Home() {
  const [news, matches, atpRankings, wtaRankings] = await Promise.all([
    getNews(),
    getMatches(),
    getRankings("ATP"),
    getRankings("WTA"),
  ]);

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="bg-tennis-green rounded-xl p-8 text-white text-center">
        <h1 className="text-3xl font-bold mb-2">TennisDaily</h1>
        <p className="text-tennis-ball/80">每日网球新闻 &middot; 比赛数据 &middot; 排名追踪</p>
      </section>

      <div className="grid md:grid-cols-2 gap-6">
        {/* News */}
        <section className="bg-white rounded-lg shadow p-5">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-tennis-dark">最新新闻</h2>
            <a
              href="/news"
              className="text-sm text-tennis-green hover:underline"
            >
              更多 &rarr;
            </a>
          </div>
          {news.length === 0 ? (
            <p className="text-gray-400 text-sm">暂无新闻</p>
          ) : (
            <ul className="space-y-3">
              {news.map((a) => (
                <li key={a.id} className="border-b pb-2 last:border-0">
                  <a
                    href={`/news/${a.id}`}
                    className="text-sm font-medium text-gray-800 hover:text-tennis-green transition"
                  >
                    {a.title}
                  </a>
                  <div className="flex gap-3 mt-1 text-xs text-gray-400">
                    {a.category && (
                      <span className="bg-green-50 text-tennis-green px-2 py-0.5 rounded">
                        {a.category}
                      </span>
                    )}
                    {a.published_at && (
                      <span>
                        {new Date(a.published_at).toLocaleDateString("zh-CN")}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Matches */}
        <section className="bg-white rounded-lg shadow p-5">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-tennis-dark">近期比赛</h2>
            <a
              href="/matches"
              className="text-sm text-tennis-green hover:underline"
            >
              更多 &rarr;
            </a>
          </div>
          {matches.length === 0 ? (
            <p className="text-gray-400 text-sm">暂无比赛数据</p>
          ) : (
            <ul className="space-y-3">
              {matches.map((m) => (
                <li
                  key={m.id}
                  className="flex items-center justify-between border-b pb-2 last:border-0 text-sm"
                >
                  <div className="flex-1">
                    <span className="font-medium text-gray-800">
                      {m.player1_name}
                    </span>
                    <span className="mx-2 text-gray-400">vs</span>
                    <span className="font-medium text-gray-800">
                      {m.player2_name}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="font-mono text-tennis-green font-bold">
                      {m.score}
                    </span>
                    <div className="text-xs text-gray-400">{m.round}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {/* Rankings */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* ATP */}
        <section className="bg-white rounded-lg shadow p-5">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-tennis-dark">ATP 排名</h2>
            <a
              href="/rankings"
              className="text-sm text-tennis-green hover:underline"
            >
              完整排名 &rarr;
            </a>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 text-xs border-b">
                <th className="text-left py-1 w-12">#</th>
                <th className="text-left py-1">球员</th>
                <th className="text-right py-1">积分</th>
              </tr>
            </thead>
            <tbody>
              {atpRankings.map((r) => (
                <tr key={r.rank} className="border-b last:border-0">
                  <td className="py-2 font-bold text-tennis-green">
                    {r.rank}
                  </td>
                  <td className="py-2 text-gray-800">{r.player_name}</td>
                  <td className="py-2 text-right font-mono text-gray-600">
                    {r.points.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* WTA */}
        <section className="bg-white rounded-lg shadow p-5">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-tennis-dark">WTA 排名</h2>
            <a
              href="/rankings?tour=WTA"
              className="text-sm text-tennis-green hover:underline"
            >
              完整排名 &rarr;
            </a>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 text-xs border-b">
                <th className="text-left py-1 w-12">#</th>
                <th className="text-left py-1">球员</th>
                <th className="text-right py-1">积分</th>
              </tr>
            </thead>
            <tbody>
              {wtaRankings.map((r) => (
                <tr key={r.rank} className="border-b last:border-0">
                  <td className="py-2 font-bold text-tennis-green">
                    {r.rank}
                  </td>
                  <td className="py-2 text-gray-800">{r.player_name}</td>
                  <td className="py-2 text-right font-mono text-gray-600">
                    {r.points.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}
