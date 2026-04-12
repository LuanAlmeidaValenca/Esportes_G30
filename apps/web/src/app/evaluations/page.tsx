"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { ClipboardEdit, Info } from "lucide-react";

interface Player {
  id: number;
  name: string;
  photo: string | null;
}

interface Sport {
  id: number;
  name: string;
  attributes: Record<string, string>;
}

export default function EvaluationsPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [sports, setSports] = useState<Sport[]>([]);

  const [selectedPlayer, setSelectedPlayer] = useState<string>("");
  const [selectedSport, setSelectedSport] = useState<string>("");
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [scores, setScores] = useState<Record<string, number>>({});

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/players").then(res => setPlayers(res.data)).catch(console.error);
    api.get("/sports").then(res => setSports(res.data)).catch(console.error);
  }, []);

  // When a sport is selected, initialize the sliders to 5 for each attribute
  useEffect(() => {
    if (selectedSport) {
      const sport = sports.find(s => s.id === Number(selectedSport));
      if (sport) {
        const initialScores: Record<string, number> = {};
        Object.keys(sport.attributes).forEach(attr => {
          initialScores[attr] = 5; // Default middle value
        });
        setScores(initialScores);
      }
    } else {
      setScores({});
    }
  }, [selectedSport, sports]);

  const handleScoreChange = (attribute: string, value: number) => {
    setScores(prev => ({ ...prev, [attribute]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlayer || !selectedSport || !date) return;

    setLoading(true);
    try {
      await api.post("/evaluations", {
        player_id: Number(selectedPlayer),
        sport_id: Number(selectedSport),
        date: date,
        scores: scores
      });
      alert("Avaliação registrada com sucesso!");
      // Reset scores back to 5
      const resetScores: Record<string, number> = {};
      Object.keys(scores).forEach(attr => resetScores[attr] = 5);
      setScores(resetScores);
    } catch (error) {
      alert("Erro ao salvar avaliação.");
    } finally {
      setLoading(false);
    }
  };

  const activeSport = sports.find(s => s.id === Number(selectedSport));

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 flex items-center gap-2">
        <ClipboardEdit size={28} /> Lançar Avaliação
      </h1>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Jogador</label>
              <select
                value={selectedPlayer}
                onChange={(e) => setSelectedPlayer(e.target.value)}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="" disabled>Selecione um jogador...</option>
                {players.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Data</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Esporte</label>
            <select
              value={selectedSport}
              onChange={(e) => setSelectedSport(e.target.value)}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option value="" disabled>Selecione a modalidade...</option>
              {sports.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          {/* Dynamic Sliders based on Sport JSON Attributes */}
          {activeSport && (
            <div className="mt-4 p-5 bg-slate-50 border border-slate-200 rounded-lg space-y-6">
              <h3 className="font-semibold text-slate-800 border-b border-slate-200 pb-2">
                Atributos ({activeSport.name})
              </h3>

              {Object.entries(activeSport.attributes).map(([attr, desc]) => (
                <div key={attr} className="flex flex-col gap-2">
                  <div className="flex justify-between items-center">
                    <label className="font-medium text-slate-700 flex items-center gap-1 group relative cursor-help">
                      {attr} <Info size={14} className="text-slate-400" />
                      <div className="absolute bottom-full left-0 mb-1 hidden group-hover:block w-48 p-2 bg-slate-800 text-white text-xs rounded shadow-lg z-10">
                        {desc}
                      </div>
                    </label>
                    <span className="font-bold text-blue-600 text-lg w-8 text-right">
                      {scores[attr]}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="1"
                    value={scores[attr] ?? 5}
                    onChange={(e) => handleScoreChange(attr, Number(e.target.value))}
                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>0 (Péssimo)</span>
                    <span>10 (Perfeito)</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !selectedPlayer || !selectedSport}
            className="mt-4 w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Registrando..." : "Registrar Avaliação"}
          </button>
        </form>
      </div>
    </div>
  );
}
