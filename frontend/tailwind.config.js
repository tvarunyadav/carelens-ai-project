/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#0284c7',
          600: '#0369a1',
          900: '#0c4a6e',
        },
        medical: {
          accent: '#0d9488',
          teal: '#14b8a6',
          slate: '#0f172a',
          card: '#1e293b',
        }
      }
    },
  },
  plugins: [],
}
