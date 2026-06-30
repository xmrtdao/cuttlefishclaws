import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

export default defineConfig({
  base: '/cuttlefishclaws/',
  plugins: [
    react(),
    {
      name: 'gh-pages-404',
      closeBundle() {
        // GH Pages SPA fallback: copy index.html to 404.html
        const dist = path.resolve(__dirname, 'dist')
        fs.copyFileSync(path.join(dist, 'index.html'), path.join(dist, '404.html'))
      }
    },
    {
      name: 'netlify-forms-inject',
      transformIndexHtml(html) {
        // Inject hidden static forms for Netlify Forms detection
        // Netlify scans built HTML for <form data-netlify="true"> at deploy time
        const forms = `
  <form name="cac-presale" data-netlify="true" netlify-honeypot="bot-field" style="display:none">
    <input type="text" name="name" />
    <input type="email" name="email" />
    <input type="text" name="type" />
    <input type="text" name="referral" />
  </form>
  <form name="investor-inquiry" data-netlify="true" netlify-honeypot="bot-field" style="display:none">
    <input type="text" name="name" />
    <input type="email" name="email" />
    <input type="text" name="amount" />
    <input type="text" name="interest" />
  </form>`
        return html.replace('</body>', `${forms}\n</body>`)
      }
    }
  ],
  build: {
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          'viz-engine': ['./src/lib/vizEngine'],
          'vendor': ['react', 'react-dom', 'react-router-dom'],
        }
      }
    },
    chunkSizeWarningLimit: 800,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
