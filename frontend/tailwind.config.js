/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
        sans: ['"DM Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        canvas: '#fafaf9',
        surface: '#ffffff',
        ink: {
          DEFAULT: '#0c0a09',
          muted: '#57534e',
          subtle: '#a8a29e',
        },
        line: '#e7e5e4',
        accent: {
          DEFAULT: '#991b1b',
          dark: '#7f1d1d',
          light: '#dc2626',
        },
        success: '#15803d',
        warning: '#a16207',
        danger: '#b91c1c',
      },
      letterSpacing: {
        tightest: '-0.04em',
      },
    },
  },
  plugins: [],
}
