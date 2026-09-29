import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this
    server: { entry: "server" },
  },
  vite: {
    preview: {
      host: "0.0.0.0",
      port: 4173,
      allowedHosts: ["testing-holtech.employer.com.br"], // ou passe `allowedHosts: true` para aceitar qualquer host
    },
  },
});