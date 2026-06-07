import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, Star } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import type { Movie } from '../types';
import Poster from '../components/Poster';
import Spinner from '../components/Spinner';
import { formatDuration } from '../utils/format';

const EASE_OUT_EXPO = [0.16, 1, 0.3, 1] as const;

const gridVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06, delayChildren: 0.05 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 22, filter: 'blur(6px)' },
  show: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: { duration: 0.55, ease: EASE_OUT_EXPO },
  },
};

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
    <div>
      <motion.div
        className="mb-9"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: EASE_OUT_EXPO }}
      >
        <p className="text-xs font-600 uppercase tracking-[0.4em] text-amber">Em cartaz</p>
        <h1 className="mt-2 font-display text-6xl leading-[0.9] tracking-marquee sm:text-7xl">
          Escolha seu <span className="text-amber">filme</span>
        </h1>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted">
          Selecione um filme para ver as sessões, escolher seus assentos no mapa interativo e
          reservar com confirmação em tempo real.
        </p>
      </motion.div>

      <motion.div
        className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4"
        variants={gridVariants}
        initial="hidden"
        animate="show"
      >
        {movies.map((movie) => (
          <motion.div key={movie.id} variants={cardVariants}>
            <Link
              to={`/movies/${movie.id}`}
              className="group block overflow-hidden rounded-xl border border-line bg-panel transition-all duration-300 hover:-translate-y-1.5 hover:border-amber/50 hover:shadow-2xl hover:shadow-amber/10"
            >
              <div className="relative aspect-[2/3] overflow-hidden">
                <div className="h-full w-full transition-transform duration-500 group-hover:scale-105">
                  <Poster title={movie.title} genre={movie.genre} url={movie.poster_url} />
                </div>
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
              </div>
              <div className="space-y-1.5 p-3">
                <h2 className="truncate font-600 leading-tight transition-colors group-hover:text-amber">
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
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
