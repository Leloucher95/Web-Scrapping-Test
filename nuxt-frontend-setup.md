# Nuxt Frontend Setup & Troubleshooting (Nuxt 4)

This doc captures the exact setup that made the frontend work and how to avoid the “header only / empty page” issue in the future.

## ✅ Requirements
- Node 18+ (LTS recommended)
- Nuxt `^4.1.2`
- Package manager: npm

## 📂 Directory structure that works
Nuxt 4 treats `app/` as the root UI directory. Put views under `app/pages/` and layouts under `app/layouts/`.

```
frontend/QuoteScrape/
├─ app/
│  ├─ app.vue                # App shell (header/nav)
│  ├─ layouts/
│  │  └─ default.vue         # Default layout with <slot />
│  └─ pages/
│     ├─ index.vue           # Route: /
│     ├─ about.vue           # Route: /about
│     └─ test.vue            # Route: /test
├─ nuxt.config.ts
└─ tailwind.config.ts
```

## 🔧 nuxt.config.ts (key parts)
```
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  pages: true, // Force file-based routing
  typescript: { typeCheck: true, strict: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/color-mode',
  ],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
      wsUrl: process.env.WS_URL || 'ws://localhost:8000/ws',
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseAnonKey: process.env.SUPABASE_ANON_KEY,
    }
  },
  nitro: {
    preset: 'node-server',
    devProxy: {
      '/api': { target: process.env.API_BASE_URL || 'http://localhost:8000', changeOrigin: true },
    }
  }
})
```

## 🧱 App shell & layouts
- `app/app.vue` should render `<NuxtLayout><NuxtPage /></NuxtLayout>`.
- `app/layouts/default.vue` should have a root wrapper and `<slot />`.

Example:
```
<!-- app/app.vue -->
<template>
  <div>
    <!-- header / navbar here -->
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>
```

```
<!-- app/layouts/default.vue -->
<template>
  <div>
    <slot />
  </div>
</template>
```

## 🎨 Tailwind CSS (no postcss.config.js)
- Use `@nuxtjs/tailwindcss`. Don’t add a `postcss.config.js` (Nuxt warns against it).
- A `tailwind.config.ts` like this works:
```
import type { Config } from 'tailwindcss'

export default {
  content: [
    './app/**/*.{vue,js,ts}',
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.{vue,js,ts}',
    './pages/**/*.{vue,js,ts}',
    './plugins/**/*.{js,ts}',
  ],
  theme: { extend: {} },
  plugins: [],
} satisfies Config
```
- If you need custom CSS, prefer adding styles directly in components or create an asset and add it to `css: []` later. For a minimal setup, let the Tailwind module manage styles (Nuxt prints “Using default Tailwind CSS file”).

## 🚑 Troubleshooting
- Symptom: Only the header shows, pages are blank, or warning “Create a Vue component in the `pages/` directory to enable `<NuxtPage>`”.
  1) Ensure your pages live in `app/pages/` (not root `pages/`).
  2) Ensure `pages: true` exists in `nuxt.config.ts`.
  3) Ensure `app/app.vue` contains `<NuxtLayout><NuxtPage /></NuxtLayout>`.
  4) Ensure `app/layouts/default.vue` exists and has a `<slot />`.
  5) Clear caches and restart:
     - `rm -rf .nuxt`
     - `npm run dev`
- Symptom: PostCSS warning about `postcss.config.js`.
  - Remove `postcss.config.js` and rely on `@nuxtjs/tailwindcss`.
- Symptom: CSS import path errors for `~/assets/...` or `@/assets/...`.
  - Prefer the Tailwind module default. If you add a CSS file later, ensure the path exists and matches your directory structure.

## 🧪 Quick sanity checks
- Create `app/pages/test.vue` with simple content and navigate to `/test`.
- Check terminal for “Vite client/server built” and “Found 0 errors”.
- Open DevTools console for runtime errors.

## 🗺️ What we fixed in this repo
- Moved pages to `app/pages/` and kept a simple `default.vue` layout.
- Wrapped `<NuxtPage />` in `<NuxtLayout>` in `app/app.vue`.
- Enabled `pages: true` in `nuxt.config.ts`.
- Removed `postcss.config.js` and let Tailwind module handle PostCSS.

## ▶️ Start
```bash
cd frontend/QuoteScrape
npm run dev
# open http://localhost:3000
```

---

# Next Steps (Roadmap)

## Frontend
- WebSocket plugin (socket.io-client) to stream scraping progress (events: `progress`, `done`, `error`).
- Wire `stores/scraping.ts` to real API (`/api/scrape/start`) and update status.
- Display quotes: use `stores/quotes.ts` with pagination and filters (topic/author).
- UI polish: loading states, toasts, error boundary, empty states.
- Env: finalize `.env` (`API_BASE_URL`, `WS_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`).

## Backend (FastAPI)
- Bootstrap FastAPI app with `/health`.
- Endpoints: `POST /api/scrape/start`, `GET /api/scrape/status/:id`.
- WebSocket endpoint `/ws` (push progress + partial results).
- Scraper module (Playwright): pagination, throttling, retries.
- Persistence: Supabase tables (quotes, jobs, job_events) + storage for images if needed.
- Tests: unit for parsing, e2e for API happy path.

## Infra & DX
- Lint/format: ESLint + Prettier (front & back).
- GitHub Actions: build + typecheck + basic tests.
- Docker (optional): docker-compose for frontend/backend.
- Docs: update README with quick start and .env templates.

If tu veux, je peux enchaîner avec le plugin WebSocket côté front et un squelette d’API côté back pour faire tourner le tout en “end-to-end” rapidement.