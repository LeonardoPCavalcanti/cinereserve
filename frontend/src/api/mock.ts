// ─────────────────────────────────────────────────────────────────────────
// Camada de DEMO (mock) da API CineReserve.
//
// Permite que o frontend rode AO VIVO no GitHub Pages sem o backend Django
// hospedado. Mantém estado em memória (status dos assentos, reservas) e
// simula o comportamento real da API — inclusive o LOCK de concorrência:
// reservar um assento o marca como "reserved" com `locked_until`, e só o
// checkout o converte em "sold". Reservar um assento já ocupado lança erro,
// exatamente como o controle de concorrência do servidor faria.
// ─────────────────────────────────────────────────────────────────────────
import type {
  CinemaSession,
  Movie,
  Reservation,
  SeatMap,
  SeatStatus,
  Ticket,
} from '../types';

const uid = () => crypto.randomUUID();
const delay = (ms = 320) => new Promise((r) => setTimeout(r, ms));

// ── Dados base ──────────────────────────────────────────────────────────
const MOVIES: Movie[] = [
  {
    id: 'm1',
    title: 'Horizonte de Eventos',
    description:
      'Uma tripulação investiga um sinal vindo de um buraco negro e descobre que o tempo a bordo já não obedece às regras que conheciam.',
    duration_minutes: 128,
    genre: 'Ficção Científica',
    director: 'A. Moreira',
    cast: 'L. Prado, M. Tavares, R. Nunes',
    poster_url: null,
    release_date: '2026-03-14',
  },
  {
    id: 'm2',
    title: 'A Última Sessão',
    description:
      'Em um cinema de rua prestes a fechar, o projecionista revive memórias que se misturam com os filmes que exibe.',
    duration_minutes: 102,
    genre: 'Drama',
    director: 'C. Beltrão',
    cast: 'J. Ferreira, P. Lima',
    poster_url: null,
    release_date: '2026-02-01',
  },
  {
    id: 'm3',
    title: 'Protocolo Vermelho',
    description:
      'Uma hacker e um ex-agente têm 72 horas para impedir que um vazamento derrube a infraestrutura de uma cidade inteira.',
    duration_minutes: 117,
    genre: 'Ação / Thriller',
    director: 'S. Andrade',
    cast: 'B. Rocha, T. Mendes',
    poster_url: null,
    release_date: '2026-04-22',
  },
  {
    id: 'm4',
    title: 'Cartas de Verão',
    description:
      'Duas estranhas trocam correspondências por um ano inteiro e descobrem que compartilham muito mais do que imaginavam.',
    duration_minutes: 96,
    genre: 'Romance',
    director: 'H. Queiroz',
    cast: 'A. Castro, V. Sales',
    poster_url: null,
    release_date: '2026-01-18',
  },
  {
    id: 'm5',
    title: 'O Jardim das Marés',
    description:
      'Animação sobre uma menina que cuida de um jardim capaz de florescer apenas quando a maré sobe.',
    duration_minutes: 89,
    genre: 'Animação',
    director: 'Estúdio Maré',
    cast: 'Vozes do elenco original',
    poster_url: null,
    release_date: '2026-05-09',
  },
  {
    id: 'm6',
    title: 'Ruído Branco',
    description:
      'Um podcaster de mistérios reais começa a receber gravações que parecem prever crimes antes que aconteçam.',
    duration_minutes: 110,
    genre: 'Suspense',
    director: 'D. Vasconcelos',
    cast: 'F. Barros, N. Pires',
    poster_url: null,
    release_date: '2026-03-28',
  },
];

const ROOMS = [
  { id: 'r1', name: 'Sala 1' },
  { id: 'r2', name: 'Sala 2' },
  { id: 'r3', name: 'IMAX' },
];

const FORMATS = ['2D', '3D', 'IMAX'];
const LANGS = ['Dublado', 'Legendado'];
const TIMES = ['14:30', '17:00', '19:45', '22:15'];

// Gera as sessões de forma determinística (3 por filme).
function buildSessions(): CinemaSession[] {
  const out: CinemaSession[] = [];
  MOVIES.forEach((movie, mi) => {
    for (let s = 0; s < 3; s++) {
      const room = ROOMS[(mi + s) % ROOMS.length];
      const time = TIMES[(mi + s) % TIMES.length];
      const date = new Date();
      date.setDate(date.getDate() + (s % 3));
      const [hh, mm] = time.split(':').map(Number);
      date.setHours(hh, mm, 0, 0);
      const end = new Date(date.getTime() + movie.duration_minutes * 60000);
      out.push({
        id: `${movie.id}-s${s}`,
        movie: { id: movie.id, title: movie.title, poster_url: movie.poster_url },
        room: { id: room.id, name: room.name },
        start_time: date.toISOString(),
        end_time: end.toISOString(),
        language: LANGS[(mi + s) % LANGS.length],
        format: room.name === 'IMAX' ? 'IMAX' : FORMATS[(mi + s) % 2],
      });
    }
  });
  return out;
}

const SESSIONS = buildSessions();

const ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
const SEATS_PER_ROW = 10;

// Hash simples e estável para "ocupar" assentos de forma determinística.
function seeded(str: string): number {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
  return h;
}

// Estado mutável dos mapas de assento, criado sob demanda por sessão.
const seatMaps = new Map<string, SeatStatus[]>();

function ensureSeatMap(sessionId: string): SeatStatus[] {
  const existing = seatMaps.get(sessionId);
  if (existing) return existing;

  const seats: SeatStatus[] = [];
  const base = seeded(sessionId);
  ROWS.forEach((row) => {
    for (let n = 1; n <= SEATS_PER_ROW; n++) {
      const label = `${row}${n}`;
      const noise = seeded(`${sessionId}:${label}`);
      // ~28% pré-ocupados (sold), distribuídos de forma estável.
      const status = (noise + base) % 100 < 28 ? 'sold' : 'available';
      seats.push({ seat_id: `${sessionId}:${label}`, row, number: n, label, status });
    }
  });
  seatMaps.set(sessionId, seats);
  return seats;
}

const reservations = new Map<string, Reservation>();

// ── "Endpoints" ─────────────────────────────────────────────────────────
export const mockApi = {
  async listMovies(): Promise<Movie[]> {
    await delay();
    return MOVIES;
  },

  async getMovie(id: string): Promise<Movie> {
    await delay(200);
    const m = MOVIES.find((x) => x.id === id);
    if (!m) throw new ApiError('Filme não encontrado', 404);
    return m;
  },

  async listSessions(movieId: string): Promise<CinemaSession[]> {
    await delay();
    return SESSIONS.filter((s) => s.movie.id === movieId);
  },

  async getSession(sessionId: string): Promise<CinemaSession> {
    await delay(160);
    const s = SESSIONS.find((x) => x.id === sessionId);
    if (!s) throw new ApiError('Sessão não encontrada', 404);
    return s;
  },

  async getSeatMap(sessionId: string): Promise<SeatMap> {
    await delay();
    const session = SESSIONS.find((x) => x.id === sessionId);
    const seats = ensureSeatMap(sessionId);
    return { session_id: sessionId, room: session?.room.name ?? '—', seats };
  },

  async createReservation(sessionId: string, seatId: string): Promise<Reservation> {
    await delay(420);
    const seats = ensureSeatMap(sessionId);
    const seat = seats.find((s) => s.seat_id === seatId);
    if (!seat) throw new ApiError('Assento inexistente', 404);
    // Controle de concorrência: assento já ocupado => 409 Conflict.
    if (seat.status !== 'available') {
      throw new ApiError('Este assento acabou de ser ocupado. Escolha outro.', 409);
    }
    seat.status = 'reserved';
    const reservation: Reservation = {
      reservation_id: uid(),
      session_id: sessionId,
      seat_id: seatId,
      seat_label: seat.label,
      locked_until: new Date(Date.now() + 5 * 60000).toISOString(),
      status: 'locked',
    };
    reservations.set(reservation.reservation_id, reservation);
    return reservation;
  },

  async checkout(reservationId: string): Promise<Ticket> {
    await delay(520);
    const reservation = reservations.get(reservationId);
    if (!reservation) throw new ApiError('Reserva expirada ou inexistente', 404);
    const seats = ensureSeatMap(reservation.session_id);
    const seat = seats.find((s) => s.seat_id === reservation.seat_id);
    if (seat) seat.status = 'sold';
    const session = SESSIONS.find((x) => x.id === reservation.session_id)!;
    reservations.delete(reservationId);
    return {
      ticket_id: uid(),
      ticket_code: `CR-${reservationId.slice(0, 8).toUpperCase()}`,
      session: {
        id: session.id,
        movie_title: session.movie.title,
        start_time: session.start_time,
        room: session.room.name,
        format: session.format,
      },
      seat_label: reservation.seat_label,
      purchased_at: new Date().toISOString(),
    };
  },
};

export class ApiError extends Error {
  status: number;
  constructor(message: string, status = 500) {
    super(message);
    this.status = status;
  }
}
