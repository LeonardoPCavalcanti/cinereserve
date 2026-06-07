import { posterGradient } from '../lib/format';

interface PosterProps {
  title: string;
  genre?: string;
  /** url opcional vinda da API; se ausente, gera um pôster por gradiente. */
  url?: string | null;
  className?: string;
}

/**
 * Pôster do filme. Se a API fornecer `poster_url`, usa a imagem; caso
 * contrário, renderiza um pôster tipográfico por gradiente (estável por
 * título) — evita imagens externas quebradas e mantém um visual coeso.
 */
export default function Poster({ title, genre, url, className = '' }: PosterProps) {
  if (url) {
    return (
      <img
        src={url}
        alt={title}
        loading="lazy"
        className={`h-full w-full object-cover ${className}`}
      />
    );
  }
  return (
    <div
      className={`flex h-full w-full flex-col justify-end p-4 ${className}`}
      style={{ background: posterGradient(title) }}
    >
      <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-transparent to-white/5" />
      <div className="relative">
        {genre && (
          <span className="mb-1 inline-block rounded bg-black/30 px-2 py-0.5 text-[0.6rem] font-600 uppercase tracking-wider text-white/80">
            {genre}
          </span>
        )}
        <h3 className="font-display text-lg font-700 leading-tight drop-shadow">{title}</h3>
      </div>
    </div>
  );
}
