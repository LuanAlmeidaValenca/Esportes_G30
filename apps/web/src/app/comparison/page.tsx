"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from "recharts";
import { Search } from "lucide-react";

export default function ComparisonPage() {
  const [players, setPlayers] = useState<any[]>([]);
  const [sports, setSports] = useState<any[]>([]);

  const [selectedSport, setSelectedSport] = useState<string>("");
  const [selectedPlayers, setSelectedPlayers] = useState<number[]>([]);

  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Distinct colors for up to 5 compared players
  const colors = ["#2563eb", "#16a34a", "#dc2626", "#d97706", "#9333ea"];

  useEffect(() => {
    api.get("/players").then(res => setPlayers(res.data)).catch(console.error);
    api.get("/sports").then(res => setSports(res.data)).catch(console.error);
  }, []);

  const togglePlayerSelection = (id: number) => {
    if (selectedPlayers.includes(id)) {
      setSelectedPlayers(selectedPlayers.filter(p => p !== id));
    } else {
      if (selectedPlayers.length < 5) {
        setSelectedPlayers([...selectedPlayers, id]);
      } else {
        alert("Máximo de 5 jogadores permitidos para comparação.");
      }
    }
  };

  const handleCompare = async () => {
    if (!selectedSport || selectedPlayers.length < 2) {
      alert("Selecione um esporte e pelo menos dois jogadores para comparar.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("/analytics/comparison", {
        sportId: selectedSport,
        playerIds: selectedPlayers
      });
      setChartData(res.data);
    } catch (error) {
      console.error(error);
      alert("Erro ao carregar dados da comparação.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Comparação de Jogadores</h1>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-8">
        <h2 className="text-lg font-semibold mb-4">1. Selecione a Modalidade</h2>
        <select
          value={selectedSport}
          onChange={(e) => setSelectedSport(e.target.value)}
          className="w-full md:w-1/2 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          <option value="">Escolha um esporte...</option>
          {sports.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>

        <h2 className="text-lg font-semibold mt-6 mb-4">2. Selecione os Jogadores (Mínimo 2, Máximo 5)</h2>
        <div className="flex flex-wrap gap-3 mb-6">
          {players.map(p => {
            const isSelected = selectedPlayers.includes(p.id);
            return (
              <button
                key={p.id}
                onClick={() => togglePlayerSelection(p.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full border transition ${
                  isSelected
                    ? "bg-blue-50 border-blue-500 text-blue-700 font-medium"
                    : "bg-white border-slate-200 text-slate-600 hover:border-blue-300"
                }`}
              >
                {p.photo ? (
                  <img src={p.photo} alt={p.name} className="w-6 h-6 rounded-full object-cover" />
                ) : (
                  <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-[10px] font-bold">
                    {p.name.charAt(0).toUpperCase()}
                  </div>
                )}
                {p.name}
              </button>
            )
          })}
        </div>

        <button
          onClick={handleCompare}
          disabled={loading || !selectedSport || selectedPlayers.length < 2}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
        >
          <Search size={18} /> {loading ? "Carregando..." : "Gerar Gráfico de Comparação"}
        </button>
      </div>

      {chartData.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[500px]">
          <h2 className="text-xl font-semibold mb-6 text-center">Gráfico Radar: Desempenho Relativo</h2>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
              <PolarGrid stroke="#e2e8f0" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 13, fontWeight: 'bold' }} />
              <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#94a3b8' }} />
              <RechartsTooltip />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />

              {/* Render a Radar line for each selected player dynamically */}
              {players.filter(p => selectedPlayers.includes(p.id)).map((p, index) => (
                <Radar
                  key={p.id}
                  name={p.name}
                  dataKey={p.name}
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.2}
                />
              ))}
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
