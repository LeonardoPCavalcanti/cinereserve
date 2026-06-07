import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider, createHashRouter } from 'react-router-dom';
import App from './App';
import MoviesPage from './pages/MoviesPage';
import MovieSessionsPage from './pages/MovieSessionsPage';
import SeatSelectionPage from './pages/SeatSelectionPage';
import CheckoutPage from './pages/CheckoutPage';
import './index.css';

// HashRouter: deep links funcionam no GitHub Pages sem configuração de servidor.
const router = createHashRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <MoviesPage /> },
      { path: 'movies/:movieId', element: <MovieSessionsPage /> },
      { path: 'sessions/:sessionId', element: <SeatSelectionPage /> },
      { path: 'checkout/:reservationId', element: <CheckoutPage /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
