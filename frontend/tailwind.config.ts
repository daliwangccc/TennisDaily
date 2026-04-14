/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        tennis: {
          green: "#2D6A4F",
          court: "#4A7C59",
          ball: "#CCFF00",
          dark: "#1B4332",
        },
      },
    },
  },
  plugins: [],
};
