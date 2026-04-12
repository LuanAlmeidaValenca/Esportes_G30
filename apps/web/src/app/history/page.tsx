"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Trash2, History } from "lucide-react";

export default function HistoryPage() {
  const [evaluations, setEvaluations] = useState<any[]>([]);
  const [players, setPlayers] = useState<any[]>([]);
  const [sports, setSports] = useState<any[]>([]);

  const [filterPlayer, setFilterPlayer] = useState<string>("");
  const [filterSport, setFilterSport] = useState<string>("");

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/players").then(res => setPlayers(res.data)).catch(console.error);
    api.get("/sports").then(res => setSports(res.data)).catch(console.error);
    fetchEvaluations();
  }, []);

  useEffect(() => {
    fetchEvaluations();
  }, [filterPlayer, filterSport]);

  const fetchEvaluations = async () => {
    setLoading(true);
    try {
      let query = "";
      if (filterPlayer) query += `player_id=${filterPlayer}&`;
      if (filterSport) query += `sport_id=${filterSport}`;

      const res = await api.get(`/evaluations?${query}`);
      setEvaluations(res.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza que deseja apagar este registro de avaliação?")) return;
    try {
      await api.delete(`/evaluations/${id}`);
      fetchEvaluations();
    } catch (error) {
      alert("Erro ao deletar avaliação.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-2">
        <History size={28} /> Histórico Geral
      </h1>

      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 mb-6 flex flex-col md:flex-row gap-4 items-center">
        <span className="font-semibold text-slate-700">Filtros:</span>
        <select
          value={filterPlayer}
          onChange={(e) => setFilterPlayer(e.target.value)}
          className="w-full md:w-auto px-3 py-2 border border-slate-300 rounded-lg focus:outline-none bg-white text-sm"
        >
          <option value="">Todos os Jogadores</option>
          {players.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>

        <select
          value={filterSport}
          onChange={(e) => setFilterSport(e.target.value)}
          className="w-full md:w-auto px-3 py-2 border border-slate-300 rounded-lg focus:outline-none bg-white text-sm"
        >
          <option value="">Todos os Esportes</option>
          {sports.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Carregando...</div>
        ) : evaluations.length === 0 ? (
          <div className="p-8 text-center text-slate-500">Nenhuma avaliação encontrada.</div>
        ) : (
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600">
                <th className="p-4 font-semibold">Data</th>
                <th className="p-4 font-semibold">Jogador</th>
                <th className="p-4 font-semibold">Modalidade</th>
                <th className="p-4 font-semibold w-1/3">Notas Registradas</th>
                <th className="p-4 font-semibold text-center w-16">Ação</th>
              </tr>
            </thead>
            <tbody>
              {evaluations.map((ev) => (
                <tr key={ev.id} className="border-b border-slate-100 hover:bg-slate-50 transition">
                  <td className="p-4 text-slate-500 font-medium">
                    {new Date(ev.date).toLocaleDateString('pt-BR', { timeZone: 'UTC' })}
                  </td>
                  <td className="p-4 font-semibold text-slate-800">{ev.player_name}</td>
                  <td className="p-4 text-blue-600 font-medium">{ev.sport_name}</td>
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(ev.scores).map(([attr, val]) => (
                        <span key={attr} className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded text-xs">
                          {attr}: <strong>{String(val)}</strong>
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="p-4 text-center">
                    <button
                      onClick={() => handleDelete(ev.id)}
                      className="text-red-500 hover:text-red-700 p-1.5 hover:bg-red-50 rounded"
                      title="Deletar avaliação"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
