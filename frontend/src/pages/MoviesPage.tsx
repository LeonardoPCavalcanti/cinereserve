import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, Star } from 'lucide-react';
import { api } from '../api/client';
import type { Movie } from '../types';
import Poster from '../components/Poster';
import Spinner from '../components/Spinner';
import { formatDuration } from '../utils/format';

/** Vitrine de filmes em cartaz — ponto de entrada do fluxo de reserva. */
export default function MoviesPage() {
  const [movies, setMovies] = useState<Movie[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listMovies()
      .then(setMovies)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="py-20 text-center text-red-400">{error}</p>;
  if (!movies) return <Spinner label="Carregando filmes…" />;

  return (
    <div className="animate-fade-up">
      <div className="mb-8">
        <p className="text-xs font-600 uppercase tracking-[0.3em] text-amber">Em cartaz</p>
        <h1 className="mt-1 font-display text-3xl font-700 sm:text-4xl">Escolha seu filme</h1>
        <p className="mt-2 max-w-xl text-sm text-muted">
          Selecione um filme para ver as sessões, escolher seus assentos no mapa interativo e
          reservar com confirmação em tempo real.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {movies.map((movie) => (
          <Link
            key={movie.id}
            to={`/movies/${movie.id}`}
            className="group overflow-hidden rounded-xl border border-line bg-panel transition-all hover:-translate-y-1 hover:border-amber/40 hover:shadow-xl hover:shadow-black/40"
          >
            <div className="relative aspect-[2/3] overflow-hidden">
              <Poster title={movie.title} genre={movie.genre} url={movie.poster_url} />
            </div>
            <div className="space-y-1.5 p-3">
              <h2 className="truncate font-600 leading-tight group-hover:text-amber">
                {movie.title}
              </h2>
              <div className="flex items-center gap-3 text-[0.7rem] text-muted">
                <span className="flex items-center gap-1">
                  <Clock size={12} /> {formatDuration(movie.duration_minutes)}
                </span>
                <span className="flex items-center gap-1">
                  <Star size={12} className="text-amber" /> {movie.genre}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
