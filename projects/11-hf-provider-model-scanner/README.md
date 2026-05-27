# Hugging Face Provider Model Scanner

A small command-line toolkit for discovering, probing, benchmarking, and reporting Hugging Face inference-provider model availability for agentic coding workflows.

It is designed for Hermes-style routing, where model promotion should be based on verified provider access, clean chat compatibility, latency, and suitability for coding-agent work, rather than hardcoded model assumptions.

## What it does

- Fetches Hugging Face inference-provider model lists.
- Supports a built-in provider list or provider auto-discovery with `--providers auto`.
- Filters models by coding and reasoning keywords.
- Probes each model through Hugging Face `InferenceClient`.
- Marks strict chat compatibility only when the model replies exactly `connected`.
- Separates clean success from uncertain responses such as reasoning text, safety text, or partial compliance.
- Records per-model probe latency in milliseconds.
- Exports CSV, JSON, and HTML reports.
- Stores reusable scan results in `reports/hf_model_availability.json`.
- Allows helper scripts to read from the JSON report instead of maintaining hardcoded model lists.
- Includes a lightweight local web server for viewing reports and summary data.

## Project layout

```text
projects/11-hf-provider-model-scanner/
├── hf_model_scanner.py              # Main scanner and report generator
├── hf_report_template.py            # HTML report template/builder
├── check_hf_models.py               # Re-checks models from the JSON report
├── list_hf_available_models.py      # Lists available models from the JSON report
├── web_report_server.py             # Local report viewer and /api/summary endpoint
├── README.md                        # This guide
└── reports/
    ├── hf_model_availability.csv
    ├── hf_model_availability.json
    └── hf_model_availability.html
```

## Requirements

Python 3.10 or newer is recommended.

Install dependencies:

```bash
pip install requests huggingface_hub rich
```

Log in to Hugging Face:

```bash
huggingface-cli login
```

Alternatively, set a token in your environment.

Linux/macOS:

```bash
export HF_TOKEN="your_token_here"
```

Windows PowerShell:

```powershell
$env:HF_TOKEN="your_token_here"
```

Do not hardcode tokens in source code.

## Run a scan

From the repository root:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --output-dir projects/11-hf-provider-model-scanner/reports
```

From inside the scanner directory:

```bash
python hf_model_scanner.py --providers auto --output-dir reports
```

The scanner writes:

```text
reports/hf_model_availability.csv
reports/hf_model_availability.json
reports/hf_model_availability.html
```

## Provider discovery

Use automatic provider discovery:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --output-dir projects/11-hf-provider-model-scanner/reports
```

If Hugging Face provider discovery is unavailable, the scanner falls back to the built-in provider list.

Scan selected providers only:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers together,groq,deepinfra --output-dir projects/11-hf-provider-model-scanner/reports
```

## Re-check models from the JSON report

`check_hf_models.py` no longer uses hardcoded model lists. It reads from:

```text
reports/hf_model_availability.json
```

Re-check a few connected models:

```bash
python projects/11-hf-provider-model-scanner/check_hf_models.py --limit 5
```

From inside the scanner directory:

```bash
python check_hf_models.py --limit 5
```

## List available models from the JSON report

`list_hf_available_models.py` also reads from:

```text
reports/hf_model_availability.json
```

Example:

```bash
python projects/11-hf-provider-model-scanner/list_hf_available_models.py
```

## Open the local web report viewer

From inside the scanner directory:

```bash
python web_report_server.py --dir reports --port 8000
```

Then open:

```text
http://localhost:8000/hf_model_availability.html
```

The server also exposes:

```text
http://localhost:8000/api/summary
```

`/api/summary` returns the JSON summary from `reports/hf_model_availability.json`.

## Output columns

| Column | Meaning |
|---|---|
| `Provider` | Hugging Face inference provider, such as `together`, `groq`, or `deepinfra`. |
| `Model` | Hugging Face model ID. |
| `Status` | Probe result. `CONNECTED` means the model replied exactly `connected`. `CONNECTED?` means the call succeeded but did not follow the exact probe. `FAILED` means the request failed. |
| `Access` | Access classification, such as `Available`, `Payment required`, `Rate limited`, `Unavailable`, or `Unknown`. |
| `Tier` | Practical model tier, such as `Premium coding`, `Deep review`, `Heavy reasoning`, or `Light fallback`. |
| `Agentic coding candidate` | Whether the model appears suitable for coding-agent use. |
| `Best context` | Suggested role inferred from the model name. |
| `Latency ms` | Probe latency in milliseconds. Empty or null where no probe completed. |
| `Note` | Probe response or compact error message. |

## JSON summary fields

The JSON report includes a `summary` object. Key fields include:

| Field | Meaning |
|---|---|
| `total_entries` | Total provider/model rows discovered. |
| `connected` | Number of clean `CONNECTED` rows. |
| `failed` | Number of failed probe rows. |
| `payment_required` | Number of rows blocked by payment or billing access. |
| `rate_limited` | Number of rows blocked by rate limits. |
| `connected_latency_p50_ms` | Median latency for clean connected models. |
| `connected_latency_p95_ms` | 95th percentile latency for clean connected models. |

## Status interpretation

### `CONNECTED`

The model returned exactly:

```text
connected
```

This is the strongest signal that the provider/model route is usable for a simple chat-completion request.

### `CONNECTED?`

The request completed, but the response was not exactly `connected`.

Examples include:

- visible reasoning text before the answer;
- a longer sentence;
- safety text;
- an empty or unusual response;
- partial compliance.

Treat this as potentially usable, but not cleanly validated.

### `FAILED`

The request failed. Use `Access` and `Note` to distinguish billing, provider access, rate limits, authentication, unavailable models, and other errors.

## Hermes / agentic coding guidance

For Hermes-style routing, start with rows matching:

```text
Status = CONNECTED
Access = Available
Agentic coding candidate = true
```

Then compare latency before assigning roles.

| Tier | Suggested role |
|---|---|
| `Premium coding` | Main coding agent or complex code repair. |
| `Deep review` | Code review, debugging, second-pass reasoning. |
| `Heavy reasoning` | Planning, architecture, fallback reasoning. |
| `Light fallback` | Cheap fallback, fast checks, small edits. |

Do not promote a model on name alone. Run it through the real Hermes loop before treating it as a reliable route.

## Useful commands

Run scan with provider auto-discovery:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --output-dir projects/11-hf-provider-model-scanner/reports
```

Run scan with fewer workers:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --workers 1 --output-dir projects/11-hf-provider-model-scanner/reports
```

Skip probing and only list matching models:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --skip-tests --output-dir projects/11-hf-provider-model-scanner/reports
```

Use custom keywords:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --keywords qwen,deepseek,coder,llama --output-dir projects/11-hf-provider-model-scanner/reports
```

Re-check a few connected models:

```bash
python projects/11-hf-provider-model-scanner/check_hf_models.py --limit 5
```

Start the web viewer:

```bash
cd projects/11-hf-provider-model-scanner
python web_report_server.py --dir reports --port 8000
```

Then open `http://127.0.0.1:8000/` (the app UI).

## Troubleshooting

### Provider auto-discovery fails

The scanner should fall back to the built-in provider list. If the result looks incomplete, run with explicit providers:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers together,groq,deepinfra --output-dir projects/11-hf-provider-model-scanner/reports
```

### Hugging Face authentication fails

Run:

```bash
huggingface-cli login
```

Then re-run the scanner.

### Payment required

The provider route exists, but your Hugging Face account may not have billing or provider access enabled.

### Rate limited

Use fewer workers:

```bash
python projects/11-hf-provider-model-scanner/hf_model_scanner.py --providers auto --workers 1 --output-dir projects/11-hf-provider-model-scanner/reports
```

### HTML report is missing latency

Make sure `hf_report_template.py` is the updated version and that the scanner is exporting the `Latency ms` field.

### Helper scripts show no models

Make sure this file exists first:

```text
projects/11-hf-provider-model-scanner/reports/hf_model_availability.json
```

Create it by running the scanner.

## Safety notes

- Keep Hugging Face tokens in environment variables or the Hugging Face CLI login store.
- Do not commit tokens or account-specific secrets.
- Treat generated reports as account-specific because they may reveal provider access, billing status, and model availability.
- Treat model availability as time-sensitive. Provider routing, pricing, access, and model names can change.
