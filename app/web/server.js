const fs = require("fs");
const http = require("http");
const path = require("path");

const root = __dirname;
const projectRoot = path.resolve(__dirname, "..", "..");
const port = Number(process.env.FRONTEND_PORT || 5173);
const apiOrigin = new URL(process.env.FRONTEND_API_ORIGIN || "http://127.0.0.1:8000");
const liveReloadClients = new Set();

const mimeTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml"
};

function sendFile(res, filePath) {
  fs.readFile(filePath, (error, content) => {
    if (error) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("No encontrado");
      return;
    }

    res.writeHead(200, {
      "Content-Type": mimeTypes[path.extname(filePath)] || "application/octet-stream"
    });
    res.end(content);
  });
}

function serveLiveReload(req, res) {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive"
  });
  res.write("event: ready\ndata: ok\n\n");
  liveReloadClients.add(res);

  req.on("close", () => {
    liveReloadClients.delete(res);
  });
}

function notifyReload() {
  liveReloadClients.forEach((res) => {
    res.write("event: reload\ndata: reload\n\n");
  });
}

let reloadTimer;
fs.watch(root, { recursive: true }, (eventType, filename) => {
  if (!filename || filename.includes("vendor")) return;
  if (!/\.(html|css|js)$/.test(filename)) return;

  clearTimeout(reloadTimer);
  reloadTimer = setTimeout(notifyReload, 120);
});

function proxyApi(req, res) {
  const options = {
    hostname: apiOrigin.hostname,
    method: req.method,
    path: req.url,
    port: apiOrigin.port || 80,
    protocol: apiOrigin.protocol,
    headers: req.headers
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on("error", () => {
    if (res.destroyed || res.writableEnded) return;
    res.writeHead(503, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ message: "Lo siento, en este momento no puedo responder. Intenta más tarde." }));
  });

  res.on("close", () => {
    if (!res.writableEnded) proxyReq.destroy();
  });

  req.pipe(proxyReq);
}

http.createServer((req, res) => {
  if (req.url === "/__live-reload") {
    serveLiveReload(req, res);
    return;
  }

  if (req.url.startsWith("/web/") || req.url === "/health") {
    proxyApi(req, res);
    return;
  }

  const urlPath = decodeURIComponent(req.url.split("?")[0]);
  if (urlPath.startsWith("/vendor/ionicons/")) {
    const vendorPath = urlPath.replace("/vendor/ionicons/", "");
    const filePath = path.normalize(path.join(projectRoot, "node_modules", "ionicons", "dist", "ionicons", vendorPath));
    const ioniconsRoot = path.join(projectRoot, "node_modules", "ionicons", "dist", "ionicons");
    if (!filePath.startsWith(ioniconsRoot)) {
      res.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Prohibido");
      return;
    }
    sendFile(res, filePath);
    return;
  }

  const filePath = path.normalize(path.join(root, urlPath === "/" ? "index.html" : urlPath));

  if (!filePath.startsWith(root)) {
    res.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Prohibido");
    return;
  }

  sendFile(res, filePath);
}).listen(port, () => {
  console.log(`Frontend listo en http://127.0.0.1:${port}`);
});
