# CineReserve — Frontend

Interface React do CineReserve: fluxo completo de reserva de assentos de cinema
consumindo a API Django REST do repositório.

**Fluxo:** Filmes em cartaz → Sessões → **Mapa de assentos interativo** → Reserva
(com lock de concorrência de 5 min) → Checkout → Ingresso com código.

## Stack

- **React 18 + Vite + TypeScript**
- **Tailwind CSS** (tema cinema dark + accent âmbar)
- **React Router** (HashRouter, compatível com GitHub Pages)
- **Lucide React** (ícones)

## Modo Demo vs. API real

O app roda em **modo demo** por padrão: uma camada de mock em memória
(`src/api/mock.ts`) simula a API — inclusive o **controle de concorrência**
(reservar um assento ocupado retorna 409). Isso permite a demo ao vivo no
GitHub Pages sem backend hospedado.

Para apontar para a API Django real, defina a variável de ambiente no build:

```bash
VITE_API_BASE=https://sua-api.com npm run build
```

Com `VITE_API_BASE` definido, o cliente (`src/api/client.ts`) passa a usar
`fetch` com JWT contra `\${VITE_API_BASE}/api/v1/...`.

## Desenvolvimento

```bash
npm install
npm run dev      # http://localhost:5173/cinereserve/
npm run build
npm run preview
```

## Estrutura

```
src/
├── api/         client (mock/real toggle) + camada de demo
├── components/  Header, Poster, SeatMap, Spinner
├── pages/       Movies, MovieSessions, SeatSelection, Checkout
├── lib/         formatação de datas/duração + pôster por gradiente
└── types.ts     tipos espelhando os serializers da API
```
