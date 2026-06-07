import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Ticket as TicketIcon, AlertTriangle } from 'lucide-react';
import { api, ApiError } from '../api/client';
import type { CinemaSession, SeatMap as SeatMapType, SeatStatus } from '../types';
import SeatMap from '../components/SeatMap';
import Spinner from '../components/Spinner';
import { formatDateTime } from '../lib/format';

/**
 * Seleção de assento + criação da reserva.
 *
 * Ao reservar, a API aplica um LOCK de concorrência: se o assento foi tomado
 * por outra pessoa nesse meio-tempo, recebemos 409 e recarregamos o mapa.
 * Em sucesso, navegamos para o checkout levando a reserva no state.
 */
export default function SeatSelectionPage() {
  const { sessionId = '' } = useParams();
  const navigate = useNavigate();

  const [session, setSession] = useState<CinemaSession | null>(null);
  const [map, setMap] = useState<SeatMapType | null>(null);
  const [selected, setSelected] = useState<SeatStatus | null>(null);
  const [reserving, setReserving] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function loadMap() {
    return api.getSeatMap(sessionId).then(setMap);
  }

  useEffect(() => {
    Promise.all([api.getSession(sessionId), api.getSeatMap(sessionId)])
      .then(([s, m]) => {
        setSession(s);
        setMap(m);
      })
      .catch((e) => setError(e.message));
  }, [sessionId]);

  async function handleReserve() {
    if (!selected) return;
    setReserving(true);
    setNotice(null);
    try {
      const reservation = await api.createReservation(sessionId, selected.seat_id);
      // Backup em sessionStorage para o checkout sobreviver a um refresh.
      sessionStorage.setItem(`cr_res_${reservation.reservation_id}`, JSON.stringify(reservation));
      navigate(`/checkout/${reservation.reservation_id}`, { state: { reservation, session } });
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : 'Falha ao reservar. Tente novamente.';
      setNotice(msg);
      setSelected(null);
      await loadMap(); // re-sincroniza o mapa (assento pode ter sido ocupado)
    } finally {
      setReserving(false);
    }
  }

  if (error) return <p className="py-20 text-center text-red-400">{error}</p>;
  if (!session || !map) return <Spinner label="Carregando mapa de assentos…" />;

  return (
    <div className="animate-fade-up">
      <Link
        to={`/movies/${session.movie.id}`}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-amber"
      >
        <ArrowLeft size={16} /> Voltar às sessões
      </Link>

      <div className="mb-6">
        <h1 className="font-display text-2xl font-700 sm:text-3xl">{session.movie.title}</h1>
        <p className="mt-1 text-sm text-muted">
          {formatDateTime(session.start_time)} · {session.room.name} · {session.format} ·{' '}
          {session.language}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        <SeatMap
          seats={map.seats}
          selectedId={selected?.seat_id ?? null}
          onSelect={(seat) => setSelected(seat)}
        />

        {/* Painel de resumo / ação */}
        <aside className="h-fit rounded-2xl border border-line bg-panel p-5 lg:sticky lg:top-24">
          <h2 className="font-display text-lg font-600">Sua seleção</h2>

          {notice && (
            <div className="mt-3 flex items-start gap-2 rounded-lg border border-amber/40 bg-amber/10 p-3 text-xs text-amber">
              <AlertTriangle size={15} className="mt-0.5 shrink-0" />
              <span>{notice}</span>
            </div>
          )}

          <div className="mt-4 flex items-center justify-between border-b border-line pb-4">
            <span className="text-sm text-muted">Assento</span>
            <span className="font-display text-2xl font-700 text-amber">
              {selected ? selected.label : '—'}
            </span>
          </div>

          <button
            type="button"
            disabled={!selected || reserving}
            onClick={handleReserve}
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-amber py-3 font-600 text-ink transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <TicketIcon size={18} />
            {reserving ? 'Reservando…' : 'Reservar assento'}
          </button>
          <p className="mt-3 text-center text-[0.7rem] leading-relaxed text-muted">
            A reserva fica bloqueada por 5 minutos para você concluir a compra.
          </p>
        </aside>
      </div>
    </div>
  );
}
