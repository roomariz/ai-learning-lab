import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { snapshotProject } from "../src/utils/files.js";

test("snapshotProject returns relative paths and exact file contents", () => {
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "ai-dev-server-snapshot-"));
  fs.mkdirSync(path.join(rootDir, "src", "routes"), { recursive: true });
  fs.mkdirSync(path.join(rootDir, "node_modules", "ignored"), { recursive: true });
  fs.mkdirSync(path.join(rootDir, ".git"), { recursive: true });
  fs.writeFileSync(path.join(rootDir, "package.json"), '{"name":"demo"}', "utf8");
  fs.writeFileSync(path.join(rootDir, "src", "server.js"), "console.log('server');", "utf8");
  fs.writeFileSync(path.join(rootDir, "src", "routes", "health.js"), "console.log('health');", "utf8");
  fs.writeFileSync(path.join(rootDir, "node_modules", "ignored", "skip.js"), "console.log('skip');", "utf8");
  fs.writeFileSync(path.join(rootDir, ".git", "config"), "[core]", "utf8");

  try {
    const snapshot = snapshotProject(rootDir, 10);

    assert.deepEqual(
      snapshot.map((file) => file.path),
      ["package.json", "src/routes/health.js", "src/server.js"],
    );
    assert.equal(snapshot[0].content, '{"name":"demo"}');
    assert.equal(snapshot[1].content, "console.log('health');");
    assert.equal(snapshot[2].content, "console.log('server');");
    assert.equal(snapshot.some((file) => file.path.includes("node_modules")), false);
    assert.equal(snapshot.some((file) => file.path.includes(".git")), false);
  } finally {
    fs.rmSync(rootDir, { recursive: true, force: true });
  }
});
