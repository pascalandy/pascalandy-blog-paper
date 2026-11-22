import { preview } from "astro";

const [port, instance] = process.argv.slice(2);

await preview({
  server: {
    host: "127.0.0.1",
    port: Number(port),
    headers: { "X-Verify-Blog-Instance": instance },
  },
  vite: { preview: { strictPort: true } },
});
