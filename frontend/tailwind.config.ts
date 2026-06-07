import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Tema cinema: fundo profundo + accent âmbar (premium/IMDb-like)
        ink: '#0b0b0f',
        panel: '#15151d',
        panel2: '#1d1d28',
        line: '#2a2a38',
        amber: '#f5c518',
        muted: '#9a9ab0',
      },
      fontFamily: {
        sans: ['Sora', 'system-ui', 'sans-serif'],
        display: ['"Bebas Neue"', 'Sora', 'sans-serif'],
      },
      letterSpacing: {
        marquee: '0.08em',
      },
      keyframes: {
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        flicker: {
          '0%, 100%': { opacity: '1' },
          '92%': { opacity: '1' },
          '94%': { opacity: '0.72' },
          '96%': { opacity: '1' },
          '98%': { opacity: '0.85' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.4s cubic-bezier(0.16,1,0.3,1) both',
        flicker: 'flicker 6s linear infinite',
      },
    },
  },
  plugins: [],
};

export default config;
