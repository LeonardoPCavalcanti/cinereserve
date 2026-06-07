// Helpers de formatação (datas, duração) e geração de pôster por gradiente.

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('pt-BR', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}h${m.toString().padStart(2, '0')}` : `${m}min`;
}

// Gera um par de cores estável a partir do título, para o pôster (sem imagens externas).
const PALETTES = [
  ['#7c3aed', '#2563eb'],
  ['#db2777', '#f59e0b'],
  ['#0891b2', '#16a34a'],
  ['#e11d48', '#7c2d12'],
  ['#4f46e5', '#0ea5e9'],
  ['#9333ea', '#db2777'],
];

export function posterGradient(seed: string): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  const [a, b] = PALETTES[h % PALETTES.length];
  const angle = 120 + (h % 90);
  return `linear-gradient(${angle}deg, ${a}, ${b})`;
}
