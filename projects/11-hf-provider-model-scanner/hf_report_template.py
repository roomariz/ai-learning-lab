from __future__ import annotations

from html import escape
from typing import Mapping, Sequence


def status_class(status: object) -> str:
    value = str(status).lower().replace("?", "-uncertain").replace(" ", "-")
    return value or "unknown"


def access_class(access: object) -> str:
    value = str(access).lower().replace(" ", "-").replace("/", "-")
    return value or "unknown"


def yes_no(value: object) -> str:
    return "Yes" if bool(value) else "No"


def build_metric_cards(summary: Mapping[str, int]) -> str:
    cards = []
    for key, value in summary.items():
        label = key.replace("_", " ").title()
        cards.append(
            f'''
            <div class="card">
                <strong>{escape(str(value))}</strong>
                <span>{escape(label)}</span>
            </div>
            '''
        )
    return "\n".join(cards)


def build_table_rows(rows: Sequence[Mapping[str, object]]) -> str:
    html_rows = []
    for row in rows:
        status = row.get("Status", "")
        access = row.get("Access", "")
        agentic = yes_no(row.get("Agentic coding candidate"))
        html_rows.append(
            f'''
            <tr class="{escape(status_class(status))} access-{escape(access_class(access))}">
                <td>{escape(str(row.get("Provider", "")))}</td>
                <td><code>{escape(str(row.get("Model", "")))}</code></td>
                <td>{escape(str(status))}</td>
                <td>{escape(str(access))}</td>
                <td>{escape(str(row.get("Tier", "")))}</td>
                <td class="agentic-{agentic.lower()}">{agentic}</td>
                <td>{escape(str(row.get("Best context", "")))}</td>
                <td>{escape(str(row.get("Note", "")))}</td>
            </tr>
            '''
        )
    return "\n".join(html_rows)


def build_html_report(
    rows: Sequence[Mapping[str, object]],
    summary: Mapping[str, int],
    username: str,
    generated_at: str,
) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hugging Face Model Availability</title>
<style>
:root {{
    --bg: #f7f7f8;
    --text: #111827;
    --muted: #6b7280;
    --panel: #ffffff;
    --line: #e5e7eb;
    --dark: #111827;
    --ok: #047857;
    --warn: #92400e;
    --bad: #b91c1c;
    --info: #1d4ed8;
}}
* {{ box-sizing: border-box; }}
body {{
    font-family: Arial, sans-serif;
    margin: 32px;
    background: var(--bg);
    color: var(--text);
}}
header {{ margin-bottom: 24px; }}
h1 {{ margin: 0 0 8px; }}
.meta {{ color: var(--muted); margin: 4px 0; }}
.cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin: 24px 0;
}}
.card {{
    background: var(--panel);
    padding: 16px 20px;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
}}
.card strong {{ display: block; font-size: 28px; }}
.card span {{ color: var(--muted); }}
table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--panel);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
}}
th, td {{
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid var(--line);
    vertical-align: top;
}}
th {{ background: var(--dark); color: white; }}
code {{ font-size: 0.92rem; }}
.connected td:nth-child(3) {{ color: var(--ok); font-weight: bold; }}
.connected td:nth-child(3)::before {{ content: "✅ "; }}
.connected-uncertain td:nth-child(3) {{ color: var(--warn); font-weight: bold; }}
.connected-uncertain td:nth-child(3)::before {{ content: "⚠️ "; }}
.failed td:nth-child(3), .list-failed td:nth-child(3) {{ color: var(--bad); font-weight: bold; }}
.failed td:nth-child(3)::before, .list-failed td:nth-child(3)::before {{ content: "❌ "; }}
.not-tested td:nth-child(3) {{ color: var(--warn); font-weight: bold; }}
.access-available td:nth-child(4) {{ color: var(--ok); font-weight: bold; }}
.access-payment-required td:nth-child(4) {{ color: var(--bad); font-weight: bold; }}
.access-rate-limited td:nth-child(4) {{ color: var(--warn); font-weight: bold; }}
.access-unknown td:nth-child(4) {{ color: var(--muted); }}
.agentic-yes {{ color: var(--info); font-weight: bold; }}
.agentic-no {{ color: var(--muted); }}
@media (max-width: 900px) {{
    body {{ margin: 16px; }}
    table {{ display: block; overflow-x: auto; }}
}}
</style>
</head>
<body>
<header>
    <h1>Hugging Face Model Availability</h1>
    <p class="meta">Logged in as: <strong>{escape(username)}</strong></p>
    <p class="meta">Generated at: {escape(generated_at)}</p>
</header>
<section class="cards">
{build_metric_cards(summary)}
</section>
<table>
<thead>
<tr>
<th>Provider</th>
<th>Model</th>
<th>Status</th>
<th>Access</th>
<th>Tier</th>
<th>Agentic</th>
<th>Best context</th>
<th>Note</th>
</tr>
</thead>
<tbody>
{build_table_rows(rows)}
</tbody>
</table>
</body>
</html>
'''
