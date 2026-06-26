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
          50: '#f5f7fa',
          100: '#e4ebf5',
          200: '#c8d6eb',
          300: '#9fbcdb',
          400: '#6f9cc8',
          500: '#487cb1',
          600: '#366192',
          700: '#2d4e77',
          800: '#274262',
          900: '#233852',
          950: '#152132',
        },
        slate: {
          750: '#1e293b',
          850: '#0f172a',
          950: '#020617',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
