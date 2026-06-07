import { Loader2 } from 'lucide-react';

/** Indicador de carregamento centralizado. */
export default function Spinner({ label = 'Carregando…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 py-20 text-muted">
      <Loader2 className="animate-spin text-amber" size={20} />
      <span className="text-sm">{label}</span>
    </div>
  );
}
