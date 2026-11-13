/**
 * Production static server for the Pravdan frontend on Databricks Apps.
 *
 * Databricks Apps runs the command from `app.yaml` (here: `npm run start`) and
 * expects the process to listen on the port it provides. This is a tiny,
 * zero-dependency Node server (built-in `http`/`fs` only — no Express) that:
 *
 *   1. Serves the Vite build output in `dist/`.
 *   2. Falls back to `index.html` for any unknown path, so client-side routes
 *      (`/`, `/admin`, `/admin/otpremanje`) work on deep links and refresh
 *      (the app uses React Router `BrowserRouter`).
 *
 * Build the app first (`npm run build`) so `dist/` exists.
 *
 * NOTE: this serves the already-built static bundle. The API base URL is baked
 * into that bundle at build time from `VITE_API_BASE_URL` (see `.env.example`),
 * so point it at the deployed backend BEFORE running `npm run build`.
 */
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, normalize, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('./dist', import.meta.url));

// Databricks provides the port to bind to; fall back for local `npm run start`.
const PORT = Number(
  process.env.DATABRICKS_APP_PORT ?? process.env.PORT ?? 8000,
);
const HOST = '0.0.0.0';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.map': 'application/json; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
};

const INDEX = join(ROOT, 'index.html');

async function sendFile(res, filePath, { cache }) {
  const body = await readFile(filePath);
  const type = MIME[extname(filePath).toLowerCase()] ?? 'application/octet-stream';
  res.writeHead(200, {
    'Content-Type': type,
    'Cache-Control': cache,
  });
  res.end(body);
}

async function sendIndex(res, status = 200) {
  const body = await readFile(INDEX);
  res.writeHead(status, {
    'Content-Type': MIME['.html'],
    // The HTML shell must never be cached, so clients always pick up new builds.
    'Cache-Control': 'no-cache',
  });
  res.end(body);
}

const server = createServer(async (req, res) => {
  try {
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405, { Allow: 'GET, HEAD' });
      res.end('Method Not Allowed');
      return;
    }

    // Decode and strip the query string, then normalise to block path traversal.
    const rawPath = decodeURIComponent((req.url ?? '/').split('?')[0]);
    const relPath = normalize(rawPath).replace(/^(\.\.(\/|\\|$))+/, '');
    const candidate = join(ROOT, relPath);

    // Resolved path must stay inside dist/.
    if (!candidate.startsWith(ROOT)) {
      await sendIndex(res, 404);
      return;
    }

    // Root → index.html.
    if (relPath === '/' || relPath === '') {
      await sendIndex(res);
      return;
    }

    try {
      const info = await stat(candidate);
      if (info.isFile()) {
        // Vite emits content-hashed asset filenames, so /assets/* is immutable.
        const cache = relPath.startsWith('/assets/')
          ? 'public, max-age=31536000, immutable'
          : 'no-cache';
        await sendFile(res, candidate, { cache });
        return;
      }
    } catch {
      // Not a real file → fall through to the SPA fallback below.
    }

    // Unknown path with no file extension (a client-side route) → SPA fallback.
    // A missing asset with an extension is a genuine 404 served as the app shell.
    await sendIndex(res, extname(relPath) ? 404 : 200);
  } catch (err) {
    console.error('[server] request failed:', err);
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Internal Server Error');
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Pravdan frontend serving ./dist on http://${HOST}:${PORT}`);
});
