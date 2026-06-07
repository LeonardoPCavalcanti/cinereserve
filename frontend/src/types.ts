// Tipos espelhando os serializers da API Django (apps/movies, sessions, seats, tickets).

export interface Movie {
  id: string;
  title: string;
  description: string;
  duration_minutes: number;
  genre: string;
  director: string;
  cast?: string;
  poster_url: string | null;
  release_date: string;
}

export interface SessionRef {
  id: string;
  title: string;
  poster_url?: string | null;
}

export interface RoomRef {
  id: string;
  name: string;
}

export interface CinemaSession {
  id: string;
  movie: SessionRef;
  room: RoomRef;
  start_time: string;
  end_time: string;
  language: string;
  format: string; // 2D, 3D, IMAX...
}

export type SeatStatusValue = 'available' | 'reserved' | 'sold';

export interface SeatStatus {
  seat_id: string;
  row: string;
  number: number;
  label: string;
  status: SeatStatusValue;
}

export interface SeatMap {
  session_id: string;
  room: string;
  seats: SeatStatus[];
}

export interface Reservation {
  reservation_id: string;
  session_id: string;
  seat_id: string;
  seat_label: string;
  locked_until: string;
  status: string;
}

export interface Ticket {
  ticket_id: string;
  ticket_code: string;
  session: {
    id: string;
    movie_title: string;
    start_time: string;
    room: string;
    format: string;
  };
  seat_label: string;
  purchased_at: string;
}
