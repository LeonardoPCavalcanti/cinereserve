// Cliente da API. Por padrão usa a camada de DEMO (mock); se `VITE_API_BASE`
// estiver definido no build, passa a falar com a API Django real via fetch+JWT.
import { mockApi, ApiError } from './mock';
import type { CinemaSession, Movie, Reservation, SeatMap, Ticket } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE as string | undefined;

/** true quando rodando sem backend (GitHub Pages) — usado para o banner de demo. */
export const IS_DEMO = !API_BASE;

// ── Implementação real (usada apenas quando VITE_API_BASE está definido) ──
async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem('cr_token');
  const res = await fetch(`${API_BASE}/api/v1${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let msg = `Erro ${res.status}`;
    try {
      const body = await res.json();
      msg = body.detail || body.message || msg;
    } catch {
      /* sem corpo JSON */
    }
    throw new ApiError(msg, res.status);
  }
  return res.json() as Promise<T>;
}

const realApi = {
  listMovies: () => http<Movie[]>('/movies/'),
  getMovie: (id: string) => http<Movie>(`/movies/${id}/`),
  listSessions: (movieId: string) => http<CinemaSession[]>(`/sessions/?movie=${movieId}`),
  getSession: (id: string) => http<CinemaSession>(`/sessions/${id}/`),
  getSeatMap: (id: string) => http<SeatMap>(`/sessions/${id}/seats/`),
  createReservation: (session_id: string, seat_id: string) =>
    http<Reservation>('/reservations/', {
      method: 'POST',
      body: JSON.stringify({ session_id, seat_id }),
    }),
  checkout: (reservation_id: string) =>
    http<Ticket>('/tickets/checkout/', {
      method: 'POST',
      body: JSON.stringify({ reservation_id }),
    }),
};

export const api = IS_DEMO ? mockApi : realApi;
export { ApiError };
