export default function Home() {
  return (
    <div className="max-w-4xl mx-auto mt-10">
      <h1 className="text-4xl font-bold mb-4">Bem-vindo ao Sports Tracker 🏆</h1>
      <p className="text-lg text-slate-600 mb-8">
        Sistema web para registrar notas e gerar dashboards comparativos de jogadores.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-2">👤 Gerencie Perfis</h2>
          <p className="text-slate-500">Cadastre jogadores com suas respectivas fotos para acompanhar a evolução.</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-2">🏅 Crie Esportes</h2>
          <p className="text-slate-500">Adicione modalidades com atributos dinâmicos e personalizados para avaliar.</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-2">📝 Avalie</h2>
          <p className="text-slate-500">Dê notas interativas utilizando sliders dinâmicos de 0 a 10.</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-2">📊 Dashboards</h2>
          <p className="text-slate-500">Gere gráficos de radar e analise as tendências dos últimos 30 dias.</p>
        </div>
      </div>
    </div>
  );
}
