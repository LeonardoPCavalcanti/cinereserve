import { Link } from 'react-router-dom';
import { Clapperboard, Github } from 'lucide-react';
import { IS_DEMO } from '../api/client';

/** Cabeçalho fixo com logo, banner de modo demo e link para o repositório. */
export default function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-ink/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-3.5">
        <Link to="/" className="group flex items-center gap-2.5">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-amber text-ink shadow-lg shadow-amber/30 transition-transform group-hover:rotate-[-6deg]">
            <Clapperboard size={20} strokeWidth={2.4} />
          </span>
          <span className="font-display text-2xl tracking-marquee">
            Cine<span className="animate-flicker text-amber">Reserve</span>
          </span>
        </Link>

        <div className="flex items-center gap-3">
          {IS_DEMO && (
            <span
              className="hidden rounded-full border border-amber/40 bg-amber/10 px-3 py-1 text-[0.68rem] font-600 uppercase tracking-wider text-amber sm:inline"
              title="Rodando com dados simulados (sem backend). Configure VITE_API_BASE para usar a API real."
            >
              Modo Demo
            </span>
          )}
          <a
            href="https://github.com/LeonardoPCavalcanti/cinereserve"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 rounded-lg border border-line px-3 py-1.5 text-sm text-muted transition-colors hover:border-amber/40 hover:text-white"
          >
            <Github size={16} />
            <span className="hidden sm:inline">Código</span>
          </a>
        </div>
      </div>
    </header>
  );
}
