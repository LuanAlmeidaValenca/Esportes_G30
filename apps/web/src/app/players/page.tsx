"use client";

import { useEffect, useState, useRef } from "react";
import api from "@/lib/api";
import { Trash2, Edit2, UserPlus, Image as ImageIcon } from "lucide-react";

interface Player {
  id: number;
  name: string;
  photo: string | null;
}

export default function PlayersPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [name, setName] = useState("");
  const [photoBase64, setPhotoBase64] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchPlayers = async () => {
    try {
      const res = await api.get("/players");
      setPlayers(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, []);

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoBase64(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmitPlayer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    setLoading(true);
    try {
      if (editingId) {
        await api.put(`/players/${editingId}`, { name, photo: photoBase64 });
      } else {
        await api.post("/players", { name, photo: photoBase64 });
      }
      handleCancelEdit();
      fetchPlayers();
    } catch (error) {
      alert("Erro ao salvar jogador. O nome pode já existir.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (player: Player) => {
    setEditingId(player.id);
    setName(player.name);
    setPhotoBase64(player.photo);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setName("");
    setPhotoBase64(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza? Todas as avaliações deste jogador serão perdidas!")) return;
    try {
      await api.delete(`/players/${id}`);
      fetchPlayers();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Gestão de Perfis</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

        {/* Form Column */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-fit">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <UserPlus size={20} /> {editingId ? "Editar Jogador" : "Novo Jogador"}
          </h2>
          <form onSubmit={handleSubmitPlayer} className="flex flex-col gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Nome do Jogador</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: João Silva"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Foto de Perfil</label>
              <div className="flex items-center gap-4">
                {photoBase64 ? (
                  <img src={photoBase64} alt="Preview" className="w-16 h-16 rounded-full object-cover border border-slate-200" />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center border border-slate-200 text-slate-400">
                    <ImageIcon size={24} />
                  </div>
                )}
                <input
                  type="file"
                  accept="image/*"
                  ref={fileInputRef}
                  onChange={handlePhotoUpload}
                  className="text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-2">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
              >
                {loading ? "Salvando..." : editingId ? "Atualizar" : "Salvar"}
              </button>
              {editingId && (
                <button
                  type="button"
                  onClick={handleCancelEdit}
                  className="flex-1 bg-slate-200 text-slate-700 py-2 rounded-lg font-medium hover:bg-slate-300 transition"
                >
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </div>

        {/* List Column */}
        <div className="md:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Jogadores Cadastrados</h2>
          {players.length === 0 ? (
            <p className="text-slate-500 italic">Nenhum jogador cadastrado ainda.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {players.map(player => (
                <div key={player.id} className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {player.photo ? (
                      <img src={player.photo} alt={player.name} className="w-12 h-12 rounded-full object-cover" />
                    ) : (
                      <div className="w-12 h-12 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold">
                        {player.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <span className="font-semibold text-slate-800">{player.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEdit(player)}
                      className="text-blue-500 hover:text-blue-700 hover:bg-blue-50 p-2 rounded-lg transition"
                      title="Editar jogador"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(player.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-lg transition"
                      title="Excluir jogador"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
