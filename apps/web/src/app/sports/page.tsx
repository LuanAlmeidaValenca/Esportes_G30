"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Trash2, Edit2, Trophy, Plus, X } from "lucide-react";

interface Sport {
  id: number;
  name: string;
  attributes: Record<string, string>;
}

export default function SportsPage() {
  const [sports, setSports] = useState<Sport[]>([]);
  const [name, setName] = useState("");
  const [attributes, setAttributes] = useState<{ name: string; description: string }[]>([
    { name: "", description: "" }
  ]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchSports = async () => {
    try {
      const res = await api.get("/sports");
      setSports(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchSports();
  }, []);

  const handleAddAttribute = () => {
    setAttributes([...attributes, { name: "", description: "" }]);
  };

  const handleRemoveAttribute = (index: number) => {
    setAttributes(attributes.filter((_, i) => i !== index));
  };

  const handleAttributeChange = (index: number, field: 'name' | 'description', value: string) => {
    const newAttributes = [...attributes];
    newAttributes[index][field] = value;
    setAttributes(newAttributes);
  };

  const handleSubmitSport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;

    const attributesObj: Record<string, string> = {};
    attributes.forEach(attr => {
      if (attr.name.trim()) {
        attributesObj[attr.name.trim()] = attr.description.trim() || "Sem descrição";
      }
    });

    if (Object.keys(attributesObj).length === 0) {
      alert("Adicione pelo menos um atributo para avaliar.");
      return;
    }

    setLoading(true);
    try {
      if (editingId) {
        await api.put(`/sports/${editingId}`, { name, attributes: attributesObj });
      } else {
        await api.post("/sports", { name, attributes: attributesObj });
      }
      handleCancelEdit();
      fetchSports();
    } catch (error) {
      alert("Erro ao salvar esporte. O nome pode já existir.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (sport: Sport) => {
    setEditingId(sport.id);
    setName(sport.name);
    // Convert JSON back to array format
    const attrsArray = Object.entries(sport.attributes).map(([key, value]) => ({
      name: key,
      description: value as string
    }));
    setAttributes(attrsArray.length > 0 ? attrsArray : [{ name: "", description: "" }]);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setName("");
    setAttributes([{ name: "", description: "" }]);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza? Todas as avaliações deste esporte serão apagadas!")) return;
    try {
      await api.delete(`/sports/${id}`);
      fetchSports();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Gestão de Esportes</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* Form Column */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Trophy size={20} /> {editingId ? "Editar Esporte" : "Novo Esporte"}
          </h2>
          <form onSubmit={handleSubmitSport} className="flex flex-col gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Nome da Modalidade</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Futebol, Vôlei, Xadrez..."
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-slate-700">Atributos Avaliativos</label>
                <button
                  type="button"
                  onClick={handleAddAttribute}
                  className="text-sm flex items-center gap-1 text-blue-600 hover:text-blue-800"
                >
                  <Plus size={16} /> Adicionar Linha
                </button>
              </div>

              <div className="flex flex-col gap-3">
                {attributes.map((attr, index) => (
                  <div key={index} className="flex gap-2 items-start">
                    <div className="flex-1">
                      <input
                        type="text"
                        value={attr.name}
                        onChange={(e) => handleAttributeChange(index, 'name', e.target.value)}
                        placeholder="Nome (ex: Passe)"
                        required
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm mb-1"
                      />
                      <input
                        type="text"
                        value={attr.description}
                        onChange={(e) => handleAttributeChange(index, 'description', e.target.value)}
                        placeholder="Dica/Explicação para quem for avaliar..."
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-600"
                      />
                    </div>
                    {attributes.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveAttribute(index)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg mt-1"
                      >
                        <X size={18} />
                      </button>
                    )}
                  </div>
                ))}
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
        <div>
          <h2 className="text-xl font-semibold mb-4">Modalidades Cadastradas</h2>
          {sports.length === 0 ? (
            <p className="text-slate-500 italic">Nenhum esporte cadastrado ainda.</p>
          ) : (
            <div className="flex flex-col gap-4">
              {sports.map(sport => (
                <div key={sport.id} className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                  <div className="flex items-center justify-between mb-3 pb-3 border-b border-slate-100">
                    <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2">
                      <Trophy size={18} className="text-amber-500" /> {sport.name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEdit(sport)}
                        className="text-blue-500 hover:text-blue-700 hover:bg-blue-50 p-2 rounded-lg transition"
                        title="Editar esporte"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button
                        onClick={() => handleDelete(sport.id)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-lg transition"
                        title="Excluir esporte"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(sport.attributes).map(([attrName, desc]) => (
                      <div key={attrName} className="bg-slate-100 px-3 py-1.5 rounded-md text-sm group relative">
                        <span className="font-semibold text-slate-700">{attrName}</span>
                        {/* Simple CSS Tooltip */}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-48 p-2 bg-slate-800 text-white text-xs rounded shadow-lg z-10">
                          {desc}
                        </div>
                      </div>
                    ))}
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
