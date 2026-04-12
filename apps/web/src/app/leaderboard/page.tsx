"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { TrendingUp, TrendingDown, Minus, Medal } from "lucide-react";
import Link from "next/link";

interface LeaderboardEntry {
  id: number;
  name: string;
  photo: string | null;
  current_score: number;
  delta: number;
  evaluations_count: number;
}

export default function LeaderboardPage() {
  const [data, setData] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/analytics/leaderboard")
      .then(res => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center mt-10">Carregando classificação...</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-2">
        <Medal size={28} className="text-amber-500" /> Classificação (Últimos 30 Dias)
      </h1>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 text-sm">
              <th className="p-4 font-semibold w-16 text-center">Pos</th>
              <th className="p-4 font-semibold">Jogador</th>
              <th className="p-4 font-semibold text-center">Avaliações</th>
              <th className="p-4 font-semibold text-right">Nota Geral</th>
              <th className="p-4 font-semibold text-right">Evolução</th>
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-8 text-center text-slate-500">
                  Sem dados nos últimos 30 dias.
                </td>
              </tr>
            ) : (
              data.map((player, index) => (
                <tr key={player.id} className="border-b border-slate-100 hover:bg-slate-50 transition">
                  <td className="p-4 text-center font-bold text-slate-400">
                    {index + 1}º
                  </td>
                  <td className="p-4">
                    <Link href={`/dashboard/${player.id}`} className="flex items-center gap-3 hover:text-blue-600">
                      {player.photo ? (
                        <img src={player.photo} alt={player.name} className="w-10 h-10 rounded-full object-cover" />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold text-xs">
                          {player.name.charAt(0).toUpperCase()}
                        </div>
                      )}
                      <span className="font-semibold">{player.name}</span>
                    </Link>
                  </td>
                  <td className="p-4 text-center text-slate-600">
                    {player.evaluations_count}
                  </td>
                  <td className="p-4 text-right font-bold text-lg">
                    {player.current_score.toFixed(1)}
                  </td>
                  <td className="p-4 text-right">
                    <div className="flex items-center justify-end gap-1">
                      {player.delta > 0 ? (
                        <><TrendingUp size={16} className="text-emerald-500" /> <span className="text-emerald-500 font-medium">+{player.delta.toFixed(1)}</span></>
                      ) : player.delta < 0 ? (
                        <><TrendingDown size={16} className="text-red-500" /> <span className="text-red-500 font-medium">{player.delta.toFixed(1)}</span></>
                      ) : (
                        <><Minus size={16} className="text-slate-400" /> <span className="text-slate-500">0.0</span></>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
