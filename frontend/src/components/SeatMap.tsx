import { motion } from 'framer-motion';
import type { SeatStatus } from '../types';

interface SeatMapProps {
  seats: SeatStatus[];
  /** seat_id atualmente selecionado pelo usuário (ainda não reservado). */
  selectedId: string | null;
  onSelect: (seat: SeatStatus) => void;
}

const ROW_ORDER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

/**
 * Mapa de assentos interativo. Agrupa os assentos por fileira e desenha a
 * grade com a "tela" no topo. Estados:
 *   - available → clicável
 *   - reserved/sold → desabilitado (ocupado)
 *   - selecionado → destaque âmbar
 */
export default function SeatMap({ seats, selectedId, onSelect }: SeatMapProps) {
  const byRow = ROW_ORDER.map((row) => ({
    row,
    seats: seats.filter((s) => s.row === row).sort((a, b) => a.number - b.number),
  })).filter((r) => r.seats.length > 0);

  return (
    <div className="rounded-2xl border border-line bg-panel/60 p-5 sm:p-7">
      {/* Tela do cinema */}
      <div className="mx-auto mb-7 w-3/4 max-w-md">
        <div className="screen-arc" />
        <p className="mt-2 text-center text-[0.62rem] uppercase tracking-[0.3em] text-muted">
          Tela
        </p>
      </div>

      <div className="flex flex-col items-center gap-2">
        {byRow.map(({ row, seats: rowSeats }) => (
          <div key={row} className="flex items-center gap-2">
            <span className="w-4 text-center text-[0.62rem] font-600 text-muted">{row}</span>
            <div className="flex gap-1.5">
              {rowSeats.map((seat) => {
                const occupied = seat.status !== 'available';
                const selected = seat.seat_id === selectedId;
                return (
                  <motion.button
                    key={seat.seat_id}
                    type="button"
                    disabled={occupied}
                    onClick={() => onSelect(seat)}
                    title={`${seat.label}${occupied ? ' · ocupado' : ''}`}
                    aria-label={`Assento ${seat.label}${occupied ? ', ocupado' : ', disponível'}`}
                    aria-pressed={selected}
                    whileHover={occupied ? undefined : { scale: 1.15 }}
                    whileTap={occupied ? undefined : { scale: 0.9 }}
                    animate={
                      selected
                        ? { scale: [1, 1.35, 1.12], transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } }
                        : { scale: 1 }
                    }
                    className={[
                      'grid h-7 w-7 place-items-center rounded-md text-[0.58rem] font-600',
                      occupied
                        ? 'cursor-not-allowed bg-line/60 text-white/20'
                        : selected
                          ? 'bg-amber text-ink shadow-lg shadow-amber/40 ring-2 ring-amber/60'
                          : 'bg-white/10 text-white/50 hover:bg-amber/30 hover:text-white',
                    ].join(' ')}
                  >
                    {seat.number}
                  </motion.button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Legenda */}
      <div className="mt-7 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[0.7rem] text-muted">
        <Legend className="bg-white/10" label="Disponível" />
        <Legend className="bg-amber" label="Selecionado" />
        <Legend className="bg-line/60" label="Ocupado" />
      </div>
    </div>
  );
}

function Legend({ className, label }: { className: string; label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className={`h-3.5 w-3.5 rounded ${className}`} />
      {label}
    </span>
  );
}
