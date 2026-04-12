"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip as RechartsTooltip } from "recharts";
import { ArrowLeft, TrendingUp, TrendingDown, Minus } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { playerId } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!playerId) return;

    api.get(`/analytics/dashboard/${playerId}`)
      .then(res => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [playerId]);

  if (loading) return <div className="text-center mt-10">Carregando dashboard...</div>;
  if (!data) return <div className="text-center mt-10 text-red-500">Erro ao carregar dados.</div>;

  const { player, kpis, history, radarData } = data;

  return (
    <div className="max-w-5xl mx-auto">
      <Link href="/leaderboard" className="flex items-center gap-2 text-slate-500 hover:text-blue-600 mb-6 transition">
        <ArrowLeft size={16} /> Voltar para Classificação
      </Link>

      {/* Header with Photo and KPIs */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-8 flex flex-col md:flex-row items-center gap-8">
        <div className="flex flex-col items-center">
          {player.photo ? (
            <img src={player.photo} alt={player.name} className="w-32 h-32 rounded-full object-cover border-4 border-slate-100 shadow-sm" />
          ) : (
            <div className="w-32 h-32 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 text-4xl font-bold shadow-sm">
              {player.name.charAt(0).toUpperCase()}
            </div>
          )}
          <h1 className="text-2xl font-bold mt-4">{player.name}</h1>
        </div>

        <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
            <p className="text-sm text-slate-500 font-medium mb-1">Média (30 dias)</p>
            <p className="text-3xl font-bold text-slate-800">{kpis.current_score.toFixed(1)}</p>
          </div>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
            <p className="text-sm text-slate-500 font-medium mb-1">Evolução</p>
            <div className="flex items-center justify-center gap-2">
              <p className="text-3xl font-bold text-slate-800">{Math.abs(kpis.delta).toFixed(1)}</p>
              {kpis.delta > 0 ? (
                <TrendingUp size={24} className="text-emerald-500" />
              ) : kpis.delta < 0 ? (
                <TrendingDown size={24} className="text-red-500" />
              ) : (
                <Minus size={24} className="text-slate-400" />
              )}
            </div>
          </div>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
            <p className="text-sm text-slate-500 font-medium mb-1">Avaliações (30 dias)</p>
            <p className="text-3xl font-bold text-slate-800">{kpis.evaluations_last_30}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Radar Chart Panel */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-6">Desempenho por Atributo (Média Geral)</h2>

          {radarData.length === 0 ? (
            <div className="h-64 flex items-center justify-center text-slate-400">
              Sem dados suficientes para o gráfico.
            </div>
          ) : (
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#94a3b8' }} />
                  <Radar name="Média" dataKey="A" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.5} />
                  <RechartsTooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* History Panel */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 overflow-y-auto max-h-[450px]">
          <h2 className="text-xl font-semibold mb-6">Histórico Recente</h2>

          {history.length === 0 ? (
            <div className="text-slate-400">Nenhuma avaliação registrada.</div>
          ) : (
            <div className="space-y-4">
              {history.slice().reverse().map((h: any, idx: number) => {
                // Calculate simple average for the run
                const values = Object.values(h.scores).map(Number);
                const avg = values.length > 0 ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1) : 0;

                return (
                  <div key={idx} className="p-4 bg-slate-50 border border-slate-100 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-slate-800">{h.sport_name}</span>
                      <span className="text-xs text-slate-500 bg-white px-2 py-1 rounded border border-slate-200">
                        {new Date(h.date).toLocaleDateString('pt-BR')}
                      </span>
                    </div>
                    <div className="flex justify-between items-center mt-2">
                       <div className="text-xs text-slate-500 truncate max-w-[70%]">
                         {Object.entries(h.scores).slice(0,3).map(([k,v]) => `${k}: ${v}`).join(' | ')}
                         {Object.keys(h.scores).length > 3 && ' ...'}
                       </div>
                       <span className="font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                         Média {avg}
                       </span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
