import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { parseAndValidateGeneration } from "../src/generate.js";

function validPackageJsonContent() {
  return JSON.stringify({
    name: "generated-express-app",
    private: true,
    type: "module",
    scripts: {
      start: "node src/server.js",
    },
    dependencies: {
      express: "^4.21.2",
    },
  });
}

function validPayload() {
  return JSON.stringify({
    summary: "Generated backend files.",
    files: [
      { path: "package.json", content: validPackageJsonContent() },
      { path: "src/server.js", content: "console.log('server');" },
      { path: "src/app.js", content: "console.log('app');" },
      { path: "src/routes/health.js", content: "console.log('health');" },
    ],
  });
}

test("accepts a valid payload", () => {
  const outputDir = path.resolve(process.cwd(), "generated");
  const expectedFiles = JSON.parse(validPayload()).files as Array<{ path: string; content: string }>;
  const result = parseAndValidateGeneration(validPayload(), outputDir);

  assert.equal(result.outputDir, outputDir);
  assert.equal(result.summary, "Generated backend files.");
  assert.deepEqual(result.files, expectedFiles);
});

test("rejects payload without package.json", () => {
  const payload = JSON.stringify({
    summary: "Generated backend files.",
    files: [
      { path: "src/server.js", content: "console.log('server');" },
      { path: "src/app.js", content: "console.log('app');" },
      { path: "src/routes/health.js", content: "console.log('health');" },
    ],
  });

  assert.throws(() => parseAndValidateGeneration(payload), /missing required file: package\.json/);
});

test("rejects payload without health route", () => {
  const payload = JSON.stringify({
    summary: "Generated backend files.",
    files: [
      { path: "package.json", content: validPackageJsonContent() },
      { path: "src/server.js", content: "console.log('server');" },
      { path: "src/app.js", content: "console.log('app');" },
    ],
  });

  assert.throws(() => parseAndValidateGeneration(payload), /missing required file: src\/routes\/health\.js/);
});

test("rejects invalid package.json rules", () => {
  const baseFiles = [
    { path: "src/server.js", content: "console.log('server');" },
    { path: "src/app.js", content: "console.log('app');" },
    { path: "src/routes/health.js", content: "console.log('health');" },
  ];

  assert.throws(
    () =>
      parseAndValidateGeneration(
        JSON.stringify({
          summary: "Generated backend files.",
          files: [
            {
              path: "package.json",
              content: JSON.stringify({
                name: "generated-express-app",
                private: true,
                scripts: { start: "node src/server.js" },
                dependencies: { express: "^4.21.2" },
              }),
            },
            ...baseFiles,
          ],
        }),
      ),
    /package\.json must use type=module/,
  );

  assert.throws(
    () =>
      parseAndValidateGeneration(
        JSON.stringify({
          summary: "Generated backend files.",
          files: [
            {
              path: "package.json",
              content: JSON.stringify({
                name: "generated-express-app",
                private: true,
                type: "module",
                dependencies: { express: "^4.21.2" },
              }),
            },
            ...baseFiles,
          ],
        }),
      ),
    /package\.json must include a start script/,
  );

  assert.throws(
    () =>
      parseAndValidateGeneration(
        JSON.stringify({
          summary: "Generated backend files.",
          files: [
            {
              path: "package.json",
              content: JSON.stringify({
                name: "generated-express-app",
                private: true,
                type: "module",
                scripts: { start: "node src/server.js" },
              }),
            },
            ...baseFiles,
          ],
        }),
      ),
    /package\.json must include express in dependencies/,
  );
});

test("rejects path traversal outside project root", () => {
  const validPackageJson = JSON.stringify({
    name: "generated-express-app",
    private: true,
    type: "module",
    scripts: { start: "node src/server.js" },
    dependencies: { express: "^4.21.2" },
  });

  assert.throws(
    () =>
      parseAndValidateGeneration(
        JSON.stringify({
          summary: "Generated backend files.",
          files: [
            { path: "package.json", content: validPackageJson },
            { path: "src/server.js", content: "console.log('server');" },
            { path: "src/app.js", content: "console.log('app');" },
            { path: "../evil.js", content: "console.log('evil');" },
          ],
        }),
      ),
    /stay within the project root/,
  );

  assert.throws(
    () =>
      parseAndValidateGeneration(
        JSON.stringify({
          summary: "Generated backend files.",
          files: [
            { path: "package.json", content: validPackageJson },
            { path: "src/server.js", content: "console.log('server');" },
            { path: "src/app.js", content: "console.log('app');" },
            { path: "/absolute/path.js", content: "console.log('evil');" },
          ],
        }),
      ),
    /stay within the project root/,
  );

  assert.throws(
    () =>
      parseAndValidateGeneration(
        JSON.stringify({
          summary: "Generated backend files.",
          files: [
            { path: "package.json", content: validPackageJson },
            { path: "src/server.js", content: "console.log('server');" },
            { path: "src/app.js", content: "console.log('app');" },
            { path: "src/../../escape.js", content: "console.log('evil');" },
          ],
        }),
      ),
    /stay within the project root/,
  );
});

test("rejects empty and non-json output", () => {
  assert.throws(() => parseAndValidateGeneration(""), /valid JSON/);
  assert.throws(() => parseAndValidateGeneration("Hello world"), /valid JSON/);
  assert.throws(() => parseAndValidateGeneration("{ invalid json"), /valid JSON|JSON|Unexpected/);
});

test("rejects an empty files array", () => {
  assert.throws(
    () =>
      parseAndValidateGeneration(
        JSON.stringify({
          summary: "Generated backend files.",
          files: [],
        }),
      ),
    /at least 3 files/,
  );
});
