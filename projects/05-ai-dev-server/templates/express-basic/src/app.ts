import express from "express";
import { registerHealthRoute } from "./routes/health.js";

export function createApp() {
  const app = express();

  registerHealthRoute(app);

  app.get("/", (_req, res) => {
    res.send("Hello World");
  });

  return app;
}
