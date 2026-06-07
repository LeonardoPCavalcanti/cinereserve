import { Outlet } from 'react-router-dom';
import Header from './components/Header';

/** Shell da aplicação: header fixo + área de rota + rodapé. */
export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-line/70 px-5 py-6 text-center text-xs text-muted">
        CineReserve · Frontend React + Vite consumindo API Django REST ·{' '}
        <a
          href="https://github.com/LeonardoPCavalcanti"
          target="_blank"
          rel="noreferrer"
          className="text-muted underline-offset-2 hover:text-amber hover:underline"
        >
          Leonardo Cavalcanti
        </a>
      </footer>
    </div>
  );
}
