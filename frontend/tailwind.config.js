/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0f2942',
          800: '#1a3c5e',
          700: '#234c73',
          600: '#2d5a87',
          500: '#3b6fa3',
          400: '#5a8ab8',
          300: '#8aafd0',
          200: '#c5d9e8',
          100: '#e3edf5',
          50: '#f1f6fa',
        },
        accent: {
          DEFAULT: '#2563eb',
          hover: '#1d4ed8',
          light: '#dbeafe',
          50: '#eff6ff',
        },
      },
      fontFamily: {
        serif: ["'Noto Serif SC'", "'Source Han Serif SC'", "'Songti SC'", 'serif'],
        sans: ["'Noto Sans SC'", '-apple-system', 'BlinkMacSystemFont', "'Segoe UI'", 'system-ui', 'sans-serif'],
        mono: ["'JetBrains Mono'", "'Fira Code'", "'Consolas'", 'monospace'],
      },
      borderRadius: {
        '2xl': '16px',
      },
    },
  },
  plugins: [],
}
