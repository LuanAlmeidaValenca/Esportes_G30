import Link from 'next/link';
import { Home, Users, Trophy, ClipboardEdit, BarChart2, PieChart, History } from 'lucide-react';

export function Sidebar() {
  return (
    <div className="w-64 h-screen bg-slate-900 text-white flex flex-col p-4 fixed left-0 top-0 overflow-y-auto">
      <div className="text-2xl font-bold mb-8 text-center border-b border-slate-700 pb-4 mt-4">
        🏆 Sports Tracker
      </div>

      <nav className="flex flex-col gap-2">
        <Link href="/" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
          <Home size={20} /> Início
        </Link>
        <Link href="/players" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
          <Users size={20} /> Perfis
        </Link>
        <Link href="/sports" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
          <Trophy size={20} /> Esportes
        </Link>
        <Link href="/evaluations" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
          <ClipboardEdit size={20} /> Avaliação
        </Link>
        <div className="my-2 border-t border-slate-700"></div>
        <Link href="/comparison" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
          <PieChart size={20} /> Comparação
        </Link>
        <Link href="/history" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
          <History size={20} /> Histórico
        </Link>
        <Link href="/leaderboard" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
          <BarChart2 size={20} /> Classificação
        </Link>
      </nav>
    </div>
  );
}
