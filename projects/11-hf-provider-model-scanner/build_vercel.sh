#!/usr/bin/env bash
set -eu

# Supports running from either:
# - repo root (PROJECT_DIR points to subfolder), or
# - scanner folder itself (PROJECT_DIR=".")
if [ -f "README.md" ] && [ -f "hf_model_scanner.py" ]; then
  PROJECT_DIR="."
else
  PROJECT_DIR="projects/11-hf-provider-model-scanner"
fi

OUT_DIR="$PROJECT_DIR/.vercel-output-static"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/src" "$OUT_DIR/reports"

cp "$PROJECT_DIR"/README.md "$OUT_DIR"/README.md
cp "$PROJECT_DIR"/*.py "$OUT_DIR"/src/

for report in hf_model_availability.json hf_model_availability.csv; do
  if [ -f "$PROJECT_DIR/reports/$report" ]; then
    cp "$PROJECT_DIR/reports/$report" "$OUT_DIR/reports/"
  fi
done

# Find Python executable
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
elif [ -f "/c/Users/rooma/AppData/Local/Programs/Python/Python312/python.exe" ]; then
  PYTHON_CMD="/c/Users/rooma/AppData/Local/Programs/Python/Python312/python.exe"
elif [ -f "/c/Users/rooma/AppData/Local/Programs/Python/Python311/python.exe" ]; then
  PYTHON_CMD="/c/Users/rooma/AppData/Local/Programs/Python/Python311/python.exe"
else
  PYTHON_CMD="python"
fi

# Compile the interactive web server template as the static demo report page
$PYTHON_CMD "$PROJECT_DIR/web_report_server.py" --dir reports --export > "$OUT_DIR/reports/hf_model_availability.html"

cat > "$OUT_DIR/index.html" <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Redirecting...</title>
  <meta http-equiv="refresh" content="0; url=/reports/hf_model_availability.html">
  <script type="text/javascript">
    window.location.replace("/reports/hf_model_availability.html");
  </script>
</head>
<body>
  <p>Redirecting to <a href="/reports/hf_model_availability.html">interactive demo dashboard</a>...</p>
</body>
</html>
HTML

