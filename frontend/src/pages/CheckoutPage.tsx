import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { CheckCircle2, Clock, Armchair, Film, Home } from 'lucide-react';
import { api } from '../api/client';
import type { Reservation, Ticket } from '../types';
import { formatDateTime } from '../utils/format';

/**
 * Confirmação da compra. Recebe a reserva via state de navegação (com backup
 * em sessionStorage para sobreviver a refresh). Mostra a contagem regressiva
 * do lock e, ao confirmar, troca a reserva por um ingresso emitido.
 */
export default function CheckoutPage() {
  const { reservationId = '' } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const reservation = useMemo<Reservation | null>(() => {
    const fromState = (location.state as { reservation?: Reservation } | null)?.reservation;
    if (fromState) return fromState;
    const cached = sessionStorage.getItem(`cr_res_${reservationId}`);
    return cached ? (JSON.parse(cached) as Reservation) : null;
  }, [location.state, reservationId]);

  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remaining, setRemaining] = useState<number>(0);

  // Contagem regressiva do lock (locked_until).
  useEffect(() => {
    if (!reservation || ticket) return;
    const tick = () => {
      const ms = new Date(reservation.locked_until).getTime() - Date.now();
      setRemaining(Math.max(0, Math.floor(ms / 1000)));
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [reservation, ticket]);

  async function handlePay() {
    setPaying(true);
    setError(null);
    try {
      setTicket(await api.checkout(reservationId));
      sessionStorage.removeItem(`cr_res_${reservationId}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha no checkout.');
    } finally {
      setPaying(false);
    }
  }

  if (!reservation && !ticket) {
    return (
      <div className="py-20 text-center">
        <p className="text-muted">Reserva não encontrada ou expirada.</p>
        <Link to="/" className="mt-3 inline-block text-amber hover:underline">
          Voltar ao início
        </Link>
      </div>
    );
  }

  // ── Ingresso emitido ──
  if (ticket) {
    return (
      <div className="mx-auto max-w-md animate-fade-up py-6">
        <div className="overflow-hidden rounded-2xl border border-line bg-panel">
          <div className="flex items-center gap-3 border-b border-dashed border-line bg-amber/10 p-5">
            <CheckCircle2 className="text-amber" />
            <div>
              <p className="font-display text-2xl tracking-marquee">Compra confirmada</p>
              <p className="text-xs text-muted">Apresente este código na entrada</p>
            </div>
          </div>
          <div className="space-y-4 p-6">
            <Row icon={<Film size={16} />} label="Filme" value={ticket.session.movie_title} />
            <Row
              icon={<Clock size={16} />}
              label="Sessão"
              value={`${formatDateTime(ticket.session.start_time)} · ${ticket.session.room} · ${ticket.session.format}`}
            />
            <Row icon={<Armchair size={16} />} label="Assento" value={ticket.seat_label} />
            <div className="rounded-xl border border-amber/30 bg-ink p-4 text-center">
              <p className="text-[0.62rem] uppercase tracking-[0.3em] text-muted">Código</p>
              <p className="mt-1 font-display text-2xl font-700 tracking-widest text-amber">
                {ticket.ticket_code}
              </p>
            </div>
          </div>
        </div>
        <Link
          to="/"
          className="mt-5 flex items-center justify-center gap-2 rounded-xl border border-line py-3 text-sm text-muted transition-colors hover:border-amber/40 hover:text-white"
        >
          <Home size={16} /> Reservar outro filme
        </Link>
      </div>
    );
  }

  // ── Resumo + confirmação ──
  const expired = remaining <= 0;
  return (
    <div className="mx-auto max-w-md animate-fade-up py-6">
      <h1 className="font-display text-4xl tracking-marquee">Confirmar compra</h1>
      <p className="mt-1 text-sm text-muted">Revise os dados e finalize sua reserva.</p>

      <div className="mt-5 rounded-2xl border border-line bg-panel p-6">
        <Row icon={<Armchair size={16} />} label="Assento" value={reservation!.seat_label} />
        <div className="my-4 h-px bg-line" />
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted">Reserva bloqueada por</span>
          <span
            className={`font-display text-xl font-700 ${expired ? 'text-red-400' : 'text-amber'}`}
          >
            {Math.floor(remaining / 60)}:{(remaining % 60).toString().padStart(2, '0')}
          </span>
        </div>

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

        <button
          type="button"
          disabled={paying || expired}
          onClick={handlePay}
          className="mt-5 w-full rounded-xl bg-amber py-3 font-600 text-ink transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {paying ? 'Processando…' : expired ? 'Reserva expirada' : 'Confirmar e pagar'}
        </button>
        {expired && (
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="mt-3 w-full text-center text-sm text-muted hover:text-amber"
          >
            Escolher assento novamente
          </button>
        )}
      </div>
    </div>
  );
}

function Row({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <span className="flex items-center gap-2 text-sm text-muted">
        {icon} {label}
      </span>
      <span className="text-right font-500">{value}</span>
    </div>
  );
}
