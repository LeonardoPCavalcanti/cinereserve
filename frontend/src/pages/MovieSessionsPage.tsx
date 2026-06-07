import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Clock, Calendar, Languages } from 'lucide-react';
import { api } from '../api/client';
import type { CinemaSession, Movie } from '../types';
import Poster from '../components/Poster';
import Spinner from '../components/Spinner';
import { formatDateTime, formatDuration, formatTime } from '../utils/format';

/** Detalhe do filme + lista de sessões disponíveis para reserva. */
export default function MovieSessionsPage() {
  const { movieId = '' } = useParams();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [sessions, setSessions] = useState<CinemaSession[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.getMovie(movieId), api.listSessions(movieId)])
      .then(([m, s]) => {
        setMovie(m);
        setSessions(s);
      })
      .catch((e) => setError(e.message));
  }, [movieId]);

  if (error) return <p className="py-20 text-center text-red-400">{error}</p>;
  if (!movie || !sessions) return <Spinner />;

  return (
    <div className="animate-fade-up">
      <Link
        to="/"
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-amber"
      >
        <ArrowLeft size={16} /> Voltar aos filmes
      </Link>

      <div className="grid gap-6 sm:grid-cols-[200px_1fr]">
        <div className="relative hidden aspect-[2/3] overflow-hidden rounded-xl border border-line sm:block">
          <Poster title={movie.title} genre={movie.genre} url={movie.poster_url} />
        </div>

        <div>
          <h1 className="font-display text-3xl font-700">{movie.title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted">
            <span className="flex items-center gap-1">
              <Clock size={14} /> {formatDuration(movie.duration_minutes)}
            </span>
            <span>{movie.genre}</span>
            <span>Dir. {movie.director}</span>
          </div>
          <p className="mt-4 max-w-2xl leading-relaxed text-white/70">{movie.description}</p>
          {movie.cast && <p className="mt-2 text-sm text-muted">Elenco: {movie.cast}</p>}

          <h2 className="mb-3 mt-8 flex items-center gap-2 font-display text-lg font-600">
            <Calendar size={18} className="text-amber" /> Sessões
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {sessions.map((s) => (
              <Link
                key={s.id}
                to={`/sessions/${s.id}`}
                className="group rounded-xl border border-line bg-panel p-4 transition-all hover:-translate-y-0.5 hover:border-amber/40"
              >
                <div className="flex items-center justify-between">
                  <span className="font-display text-2xl font-700 group-hover:text-amber">
                    {formatTime(s.start_time)}
                  </span>
                  <span className="rounded border border-amber/40 bg-amber/10 px-2 py-0.5 text-[0.62rem] font-700 uppercase text-amber">
                    {s.format}
                  </span>
                </div>
                <p className="mt-1 text-xs text-muted">{formatDateTime(s.start_time)}</p>
                <div className="mt-3 flex items-center justify-between text-xs text-muted">
                  <span>{s.room.name}</span>
                  <span className="flex items-center gap-1">
                    <Languages size={12} /> {s.language}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
