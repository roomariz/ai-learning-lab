#!/usr/bin/env bash
set -eu

PROJECT_DIR="projects/11-hf-provider-model-scanner"
OUT_DIR="$PROJECT_DIR/.vercel-output-static"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/src" "$OUT_DIR/reports"

cp "$PROJECT_DIR"/README.md "$OUT_DIR"/README.md
cp "$PROJECT_DIR"/*.py "$OUT_DIR"/src/

for report in hf_model_availability.html hf_model_availability.json hf_model_availability.csv; do
  if [ -f "$PROJECT_DIR/reports/$report" ]; then
    cp "$PROJECT_DIR/reports/$report" "$OUT_DIR/reports/"
  fi
done

cat > "$OUT_DIR/index.html" <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HF Provider Model Scanner</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #172033;
      --muted: #5f6b7a;
      --line: #d8dde6;
      --accent: #f45d22;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #090d14;
        --panel: #111827;
        --text: #eef2f8;
        --muted: #a3adba;
        --line: #263244;
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }
    main {
      max-width: 980px;
      margin: 0 auto;
      padding: 48px 20px;
    }
    header {
      border-bottom: 1px solid var(--line);
      padding-bottom: 24px;
      margin-bottom: 28px;
    }
    h1 {
      margin: 0 0 12px;
      font-size: clamp(32px, 6vw, 56px);
      line-height: 1;
      letter-spacing: 0;
    }
    p { color: var(--muted); max-width: 720px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
      margin: 28px 0;
    }
    a.card {
      display: block;
      min-height: 120px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: inherit;
      text-decoration: none;
    }
    a.card:hover { border-color: var(--accent); }
    .card strong { display: block; margin-bottom: 8px; }
    .card span { color: var(--muted); }
    code {
      display: block;
      overflow-x: auto;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--text);
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>HF Provider Model Scanner</h1>
      <p>Deployment scoped to <strong>projects/11-hf-provider-model-scanner</strong>. This page exposes only the scanner project files and any generated report artifacts present at build time.</p>
    </header>

    <section class="grid" aria-label="Project links">
      <a class="card" href="/README.md"><strong>README</strong><span>Usage, setup, report format, and scanner workflow.</span></a>
      <a class="card" href="/src/hf_model_scanner.py"><strong>Main scanner</strong><span>Provider discovery, probes, and report generation.</span></a>
      <a class="card" href="/reports/hf_model_availability.html"><strong>HTML report</strong><span>Available when report artifacts are generated before deployment.</span></a>
      <a class="card" href="/reports/hf_model_availability.json"><strong>JSON report</strong><span>Reusable scanner results for automation.</span></a>
    </section>

    <p>Run locally from the repository root:</p>
    <code>python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --output-dir projects/11-hf-provider-model-scanner/reports</code>
  </main>
</body>
</html>
HTML
