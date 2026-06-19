import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}', './app/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'hsl(var(--bg))',
        fg: 'hsl(var(--fg))',
        card: 'hsl(var(--card))',
        cardFg: 'hsl(var(--card-fg))',
        brand: {
          50: '#eefdf6',
          100: '#d7f8e6',
          200: '#b0f0ce',
          300: '#78e3af',
          400: '#3fcd8a',
          500: '#18a96c',
          600: '#118557',
          700: '#0f6947',
          800: '#0f543b',
          900: '#0d4532',
        },
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(24, 169, 108, 0.2), 0 20px 60px rgba(15, 84, 59, 0.18)',
      },
      backgroundImage: {
        'grid-faint': 'linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};

export default config;
