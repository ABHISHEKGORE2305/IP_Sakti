import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Simple MIME map so we can serve legacy frontend files with correct Content-Type
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.json': 'application/json',
  '.svg':  'image/svg+xml',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico':  'image/x-icon',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),

    // Serve the existing static frontend/ folder under /frontend/* in dev
    // so that href="/frontend/index.html" works during `npm run dev`.
    // Production / nginx: both sih_frontend_antigrav/dist and frontend/ live
    // under the same web root, so /frontend/index.html resolves naturally.
    {
      name: 'serve-legacy-frontend',
      configureServer(server) {
        server.middlewares.use('/frontend', (req, res, next) => {
          const urlPath = req.url === '/' ? '/index.html' : req.url
          const filePath = path.resolve(__dirname, '../frontend', urlPath.replace(/^\//, ''))
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const ext = path.extname(filePath).toLowerCase()
            res.setHeader('Content-Type', MIME_TYPES[ext] || 'application/octet-stream')
            res.end(fs.readFileSync(filePath))
          } else {
            next()
          }
        })
      },
    },
  ],
})
