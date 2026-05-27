from __future__ import annotations

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tiny local web server for scanner reports.")
    parser.add_argument("--dir", default="reports", help="Directory to serve (default: reports).")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000).")
    parser.add_argument(
        "--no-auto-reload",
        action="store_true",
        help="Disable automatic server restart when web_report_server.py changes.",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export the generated interactive HTML to stdout and exit.",
    )
    return parser.parse_args()


def html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def source_version() -> str:
    return str(Path(__file__).stat().st_mtime_ns)


def build_index(report_dir: Path) -> bytes:
    files = sorted([p for p in report_dir.glob("*") if p.is_file()], key=lambda p: p.name)
    links = "\n".join(
        f'<li><a href="/files/{html_escape(p.name)}">{html_escape(p.name)}</a></li>'
        for p in files
    )
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark light">
  <title>HF Model Scanner</title>
  <style>
    :root {
      --bg0: #070a12;
      --bg1: #0b1220;
      --panel: rgba(255,255,255,.06);
      --panel2: rgba(255,255,255,.04);
      --stroke: rgba(255,255,255,.10);
      --text: rgba(255,255,255,.92);
      --muted: rgba(255,255,255,.62);
      --muted2: rgba(255,255,255,.45);
      --shadow: 0 10px 32px rgba(0,0,0,.35);
      --shadow2: 0 6px 18px rgba(0,0,0,.25);
      --radius: 16px;
      --radius2: 12px;
      --accent: #ff5a1f;
      --ok: #34d399;
      --warn: #fbbf24;
      --bad: #fb7185;
      --link: #93c5fd;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Sans", "Liberation Sans", sans-serif;
      --gap: clamp(12px, 2vw, 18px);
    }

    * { box-sizing: border-box; scrollbar-width: thin; scrollbar-color: rgba(255,90,31,.62) rgba(255,255,255,.07); }
    *::-webkit-scrollbar { width: 10px; height: 10px; }
    *::-webkit-scrollbar-track {
      background: rgba(255,255,255,.06);
      border-radius: 999px;
    }
    *::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, rgba(255,90,31,.78), rgba(147,197,253,.42));
      border: 2px solid rgba(11,18,32,.92);
      border-radius: 999px;
    }
    *::-webkit-scrollbar-thumb:hover {
      background: linear-gradient(180deg, rgba(255,90,31,.92), rgba(147,197,253,.58));
    }
    html, body { width: 100%; height: 100%; }
    body {
      margin: 0;
      font-family: var(--sans);
      color: var(--text);
      background:
        radial-gradient(1200px 600px at 20% -10%, rgba(255,90,31,.18), transparent 55%),
        radial-gradient(900px 500px at 90% 10%, rgba(147,197,253,.12), transparent 50%),
        radial-gradient(700px 520px at 60% 120%, rgba(52,211,153,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
      overflow: hidden;
    }

    a { color: var(--link); text-decoration: none; }
    a:hover { text-decoration: underline; }

    .wrap {
      width: 100%;
      max-width: none;
      margin: 0 auto;
      padding: 8px;
      height: 100dvh;
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 8px;
      overflow: hidden;
    }
    header.appbar {
      display:flex; align-items:center; justify-content:space-between; gap: 12px;
      padding: 8px 10px;
      border: 1px solid var(--stroke);
      background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
      border-radius: var(--radius);
      box-shadow: var(--shadow2);
      backdrop-filter: blur(10px);
      position: relative;
      z-index: 100;
      overflow: visible;
    }
    .brand { display:flex; align-items:center; gap: 10px; min-width: 240px; }
    .logo {
      width: 32px; height: 32px; border-radius: 10px;
      background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.18), rgba(255,255,255,.06)),
                  linear-gradient(135deg, rgba(255,90,31,.85), rgba(147,197,253,.35));
      border: 1px solid rgba(255,255,255,.18);
      box-shadow: 0 8px 22px rgba(255,90,31,.18);
    }
    .brand h1 { margin: 0; font-size: 15px; letter-spacing: .2px; }
    .brand p { margin: 0; color: var(--muted); font-size: 11px; }
    .top-actions { display:flex; gap: 8px; align-items:center; justify-content:flex-end; flex-wrap: wrap; }

    .pill {
      font-size: 12px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--stroke);
      background: rgba(255,255,255,.05);
      color: var(--muted);
      display:inline-flex;
      gap: 6px;
      align-items:center;
      white-space: nowrap;
    }
    .pill b { color: var(--text); font-weight: 600; }

    .btn {
      border: 1px solid rgba(255,255,255,.14);
      background: rgba(255,255,255,.06);
      color: var(--text);
      border-radius: 12px;
      padding: 8px 10px;
      cursor: pointer;
      box-shadow: 0 10px 24px rgba(0,0,0,.18);
      transition: transform .08s ease, background .2s ease, border-color .2s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
    }
    .btn:hover { background: rgba(255,255,255,.09); border-color: rgba(255,255,255,.22); }
    .btn:active { transform: translateY(1px); }
    .btn:disabled { opacity: .55; cursor: not-allowed; }
    .btn.primary {
      background: linear-gradient(180deg, rgba(255,90,31,.92), rgba(255,90,31,.65));
      border-color: rgba(255,90,31,.35);
      color: #0b1220;
      font-weight: 700;
    }
    .btn.primary:hover { background: linear-gradient(180deg, rgba(255,90,31,.96), rgba(255,90,31,.72)); }

    details.download-menu {
      position: relative;
      z-index: 30;
    }
    details.download-menu summary {
      list-style: none;
    }
    details.download-menu summary::-webkit-details-marker { display: none; }
    details.download-menu summary::after {
      content: "▾";
      font-size: 11px;
      color: var(--muted);
      margin-left: 2px;
    }
    details.download-menu[open] summary {
      background: rgba(255,255,255,.10);
      border-color: rgba(255,255,255,.24);
    }
    details.download-menu[open] summary::after { content: "▴"; }
    .download-menu ul {
      position: absolute;
      right: 0;
      top: calc(100% + 8px);
      width: min(320px, calc(100vw - 36px));
      max-height: 280px;
      overflow: auto;
      margin: 0;
      padding: 8px;
      list-style: none;
      border: 1px solid rgba(255,255,255,.14);
      border-radius: 14px;
      background: rgba(11,18,32,.96);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
      z-index: 9999;
    }
    .download-menu li + li { margin-top: 4px; }
    .download-menu a {
      display: block;
      padding: 9px 10px;
      border-radius: 10px;
      color: rgba(255,255,255,.84);
      font-family: var(--mono);
      font-size: 12px;
      line-height: 1.35;
      overflow-wrap: anywhere;
      text-decoration: none;
    }
    .download-menu a:hover {
      background: rgba(255,255,255,.075);
      color: var(--text);
      text-decoration: none;
    }

    main.grid {
      display:grid;
      grid-template-columns: 280px 1fr;
      gap: 8px;
      min-height: 0;
      height: 100%;
      align-items: stretch;
      position: relative;
      z-index: 1;
      overflow: hidden;
    }

    section.card {
      border: 1px solid var(--stroke);
      background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.035));
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
      overflow: clip;
      min-height: 0;
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    section.results-card .bd {
      flex: 1 1 auto;
      max-height: none;
    }
    section.overview-card .bd { overflow: auto; }
    .card .hd { padding: 14px 16px 10px; border-bottom: 1px solid rgba(255,255,255,.08); }
    .card .hd h2 { margin: 0; font-size: 14px; letter-spacing: .2px; }
    .card .hd p { margin: 6px 0 0; color: var(--muted); font-size: 12px; }
    .card .bd {
      padding: 12px 12px 14px;
      min-height: 0;
      display: flex;
      flex-direction: column;
    }
    .overview-card .hd { padding: 10px 12px 8px; }
    .overview-card .bd { padding: 8px 8px 10px; }

    .metrics {
      display:grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 6px;
      margin-top: 6px;
    }
    .metric {
      border: 1px solid rgba(255,255,255,.10);
      border-radius: 8px;
      background: rgba(255,255,255,.045);
      padding: 6px 7px;
      min-height: 40px;
    }
    .metric strong { display:block; font-size: 15px; letter-spacing: .2px; line-height: 1.15; }
    .metric span { color: var(--muted); font-size: 9px; text-transform: uppercase; letter-spacing: .05em; line-height: 1.25; }
    .metric.skeleton strong, .metric.skeleton span { background: rgba(255,255,255,.07); color: transparent; border-radius: 8px; }
    .metric.skeleton strong { width: 70%; height: 18px; margin-bottom: 8px; }
    .metric.skeleton span { width: 85%; height: 12px; display:block; }

    .toolbar {
      display:flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: end;
    }
    .field { display:flex; flex-direction: column; gap: 6px; min-width: 180px; }
    .field label { font-size: 11px; color: var(--muted); letter-spacing: .08em; text-transform: uppercase; }
    input, select {
      width: 100%;
      background: rgba(0,0,0,.18);
      border: 1px solid rgba(255,255,255,.14);
      color: var(--text);
      border-radius: 12px;
      padding: 8px 10px;
      outline: none;
    }
    input::placeholder { color: rgba(255,255,255,.42); }
    input:focus, select:focus { border-color: rgba(255,90,31,.45); box-shadow: 0 0 0 3px rgba(255,90,31,.12); }
    select option { background: #0b1220; color: var(--text); }

	    .table-wrap {
	      overflow: auto;
	      flex: 1 1 auto;
	      min-height: 0;
	      max-height: none;
	      margin-top: 8px;
	      border-radius: 14px;
	      border: 1px solid rgba(255,255,255,.10);
	    }
	    .table-wrap { outline: none; overscroll-behavior: contain; }
	    .table-wrap:focus { box-shadow: 0 0 0 3px rgba(255,90,31,.16); border-color: rgba(255,90,31,.35); }
	    .table-wrap { -webkit-overflow-scrolling: touch; scrollbar-gutter: stable both-edges; }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    col.provider-col { width: 7%; }
    col.model-col { width: 20%; }
    col.status-col { width: 12%; }
    col.access-col { width: 11%; }
    col.tier-col { width: 12%; }
    col.agentic-col { width: 7%; }
    col.latency-col { width: 9%; }
    col.note-col { width: 22%; }
    th, td { padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,.08); vertical-align: top; overflow: hidden; }
    th {
      position: sticky; top: 0;
      background: rgba(11,18,32,.92);
      backdrop-filter: blur(10px);
      z-index: 10;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .12em;
      color: rgba(255,255,255,.78);
    }
    tbody tr:hover td { background: rgba(255,255,255,.03); }
    td code { font-family: var(--mono); font-size: 12px; color: rgba(255,255,255,.86); }
    td.note { color: var(--muted); word-break: break-word; overflow: hidden; text-overflow: ellipsis; }
    td.lat { text-align: right; white-space: nowrap; color: rgba(255,255,255,.78); }
    .badge {
      display:inline-flex; align-items:center; gap:6px;
      border-radius: 999px;
      padding: 5px 10px;
      border: 1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.045);
      font-size: 12px;
      white-space: nowrap;
    }
    .b-ok { color: var(--ok); border-color: rgba(52,211,153,.25); background: rgba(52,211,153,.08); }
    .b-warn { color: var(--warn); border-color: rgba(251,191,36,.22); background: rgba(251,191,36,.08); }
    .b-bad { color: var(--bad); border-color: rgba(251,113,133,.22); background: rgba(251,113,133,.08); }

    .state {
      border: 1px dashed rgba(255,255,255,.18);
      border-radius: 16px;
      padding: 14px;
      background: rgba(0,0,0,.16);
      color: var(--muted);
    }
    .state strong { color: var(--text); }
    .toast {
      position: fixed;
      right: 16px;
      bottom: 16px;
      padding: 12px 12px;
      border-radius: 14px;
      background: rgba(11,18,32,.88);
      border: 1px solid rgba(255,255,255,.14);
      color: var(--text);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
      max-width: min(420px, calc(100vw - 32px));
      display:none;
    }
    .toast.show { display:block; }
    .toast small { color: var(--muted); display:block; margin-top:4px; }

    .k { font-family: var(--mono); font-size: 12px; padding: 1px 6px; border-radius: 7px; border: 1px solid rgba(255,255,255,.18); background: rgba(0,0,0,.22); color: rgba(255,255,255,.84); }

    @media (max-width: 1050px) {
      body { overflow: auto; }
      .wrap { height: auto; min-height: 100dvh; overflow: visible; }
      main.grid { grid-template-columns: 1fr; }
      section.results-card .bd { max-height: none; }
      .table-wrap { min-height: 320px; max-height: 65vh; }
    }

    @media (max-height: 780px) {
      .metric strong { font-size: 14px; }
      .metric { min-height: 38px; }
    }

    .overview-card .metrics {
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header class="appbar" aria-label="App header">
      <div class="brand">
        <div class="logo" aria-hidden="true"></div>
        <div>
          <h1>HF Model Scanner</h1>
          <p>Scan provider routes • benchmark latency • filter results</p>
        </div>
      </div>
      <div class="top-actions">
        <span id="status" class="pill" role="status" aria-live="polite">idle</span>
        <button id="runBtn" class="btn primary" type="button" aria-label="Run scan (fetch latest)">Run scan</button>
        <details class="download-menu">
          <summary class="btn" aria-label="Open artifact downloads">Artifacts</summary>
          <ul>__FILES__</ul>
        </details>
      </div>
    </header>

    <main class="grid" aria-label="Dashboard">
      <section class="card overview-card" aria-label="Run scan and metrics">
        <div class="hd">
          <h2>Overview</h2>
        </div>
        <div class="bd">
          <div class="state" id="emptyState" style="display:none">
            <strong>No report found.</strong>
            <div style="margin-top:6px">Click <span class="k">Run scan</span> to generate <code style="font-family:var(--mono)">reports/hf_model_availability.json</code>.</div>
          </div>
          <div id="metrics" class="metrics" aria-label="Metrics" style="grid-template-columns: repeat(2, minmax(0, 1fr));"></div>
        </div>
      </section>

      <section class="card results-card" aria-label="Filters and results">
        <div class="hd">
          <h2>Models</h2>
          <p><span id="count">Loading…</span></p>
        </div>
        <div class="bd">
          <div class="toolbar" role="region" aria-label="Filters">
            <div class="field" style="min-width:240px">
              <label for="q">Search</label>
              <input id="q" type="search" placeholder="e.g. qwen3, deepseek, llama…" autocomplete="off" />
            </div>
            <div class="field">
              <label for="provider">Provider</label>
              <select id="provider"><option value="">All</option></select>
            </div>
            <div class="field">
              <label for="statusSel">Status</label>
              <select id="statusSel"><option value="">All</option></select>
            </div>
            <div class="field">
              <label for="access">Access</label>
              <select id="access"><option value="">All</option></select>
            </div>
            <div class="field" style="min-width:140px">
              <label for="agentic">Agentic</label>
              <select id="agentic">
                <option value="">All</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>
            <div class="field" style="min-width:160px">
              <label for="sort">Sort</label>
              <select id="sort">
                <option value="latency">Latency</option>
                <option value="model">Model</option>
                <option value="provider">Provider</option>
              </select>
            </div>
          </div>

          <div id="tableState" class="state" style="margin-top:12px; display:none"></div>

	          <div id="tableWrap" class="table-wrap" aria-label="Results table" tabindex="0">
	            <table>
              <colgroup>
                <col class="provider-col">
                <col class="model-col">
                <col class="status-col">
                <col class="access-col">
                <col class="tier-col">
                <col class="agentic-col">
                <col class="latency-col">
                <col class="note-col">
              </colgroup>
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Model</th>
                  <th>Status</th>
                  <th>Access</th>
                  <th>Tier</th>
                  <th>Agentic</th>
                  <th style="text-align:right">Latency</th>
                  <th>Note</th>
                </tr>
              </thead>
              <tbody id="tbody"></tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  </div>

  <div id="toast" class="toast" role="status" aria-live="polite"></div>
  <script>
    const statusEl = document.getElementById('status');
    const btn = document.getElementById('runBtn');
    const metricsEl = document.getElementById('metrics');
    const tbody = document.getElementById('tbody');
    const countEl = document.getElementById('count');
	    const emptyStateEl = document.getElementById('emptyState');
	    const tableStateEl = document.getElementById('tableState');
	    const toastEl = document.getElementById('toast');
	    const tableWrapEl = document.getElementById('tableWrap');

    const qEl = document.getElementById('q');
    const providerEl = document.getElementById('provider');
    const statusSelEl = document.getElementById('statusSel');
    const accessEl = document.getElementById('access');
    const agenticEl = document.getElementById('agentic');
    const sortEl = document.getElementById('sort');

    let DATA = null;
    const SOURCE_VERSION = '__SOURCE_VERSION__';
    let isStatic = false;

    function enableStaticMode() {
      if (isStatic) return;
      isStatic = true;
      if (btn) btn.style.display = 'none';
      if (statusEl) {
        statusEl.innerHTML = '<b>static demo</b><span style="color:var(--muted2)">— generated from last scan</span>';
      }
      const links = document.querySelectorAll('.download-menu a');
      links.forEach(a => {
        const href = a.getAttribute('href');
        if (href && href.startsWith('/files/')) {
          a.setAttribute('href', './' + href.substring(7));
        }
      });
    }

    function uniq(values) {
      return Array.from(new Set(values.filter(Boolean))).sort();
    }

    function opt(select, value) {
      const o = document.createElement('option');
      o.value = value;
      o.textContent = value;
      select.appendChild(o);
    }

    function showToast(title, detail) {
      toastEl.innerHTML = `<strong>${title}</strong>${detail ? `<small>${detail}</small>` : ''}`;
      toastEl.classList.add('show');
      setTimeout(() => toastEl.classList.remove('show'), 3600);
    }

    function badge(text, kind) {
      const cls = kind === 'ok' ? 'badge b-ok' : (kind === 'bad' ? 'badge b-bad' : 'badge b-warn');
      return `<span class="${cls}">${text}</span>`;
    }

    function statusBadge(status) {
      const s = String(status || '');
      if (s.startsWith('CONNECTED')) return badge(s, 'ok');
      if (s.includes('FAILED')) return badge(s, 'bad');
      return badge(s || '-', 'warn');
    }

    function accessBadge(access) {
      const a = String(access || '');
      if (a === 'Available') return badge('Available', 'ok');
      if (a === 'Payment required') return badge('Payment required', 'bad');
      if (a === 'Rate limited') return badge('Rate limited', 'warn');
      return badge(a || 'Unknown', 'warn');
    }

    function renderMetricSkeleton() {
      metricsEl.innerHTML = '';
      emptyStateEl.style.display = 'none';
      for (let i = 0; i < 8; i++) {
        const d = document.createElement('div');
        d.className = 'metric skeleton';
        d.innerHTML = `<strong>000</strong><span>loading</span>`;
        metricsEl.appendChild(d);
      }
    }

    function setTableState(kind, title, detail) {
      if (!kind) {
        tableStateEl.style.display = 'none';
        tableStateEl.innerHTML = '';
        return;
      }
      tableStateEl.style.display = 'block';
      const extra = detail ? `<div style="margin-top:6px;color:rgba(255,255,255,.5)">${detail}</div>` : '';
      tableStateEl.innerHTML = `<strong>${title}</strong>${extra}`;
    }

    function renderMetrics(summary) {
      metricsEl.innerHTML = '';
      if (!summary) return;
      for (const [k,v] of Object.entries(summary)) {
        const d = document.createElement('div');
        d.className = 'metric';
        d.innerHTML = `<strong>${String(v)}</strong><span>${k.replaceAll('_',' ')}</span>`;
        metricsEl.appendChild(d);
      }
    }

    function renderTable() {
      if (!DATA) return;
      const q = (qEl.value || '').toLowerCase().trim();
      const provider = providerEl.value;
      const statusV = statusSelEl.value;
      const accessV = accessEl.value;
      const agenticV = agenticEl.value;
      const sortV = sortEl.value;

      let rows = DATA.rows || [];
      const totalAll = rows.length;
      rows = rows.filter(r => {
        if (q && !String(r.model||'').toLowerCase().includes(q)) return false;
        if (provider && String(r.provider||'') !== provider) return false;
        if (statusV && String(r.status||'') !== statusV) return false;
        if (accessV && String(r.access||'') !== accessV) return false;
        if (agenticV) {
          const a = !!r.agentic_coding_candidate;
          if (agenticV === 'true' && !a) return false;
          if (agenticV === 'false' && a) return false;
        }
        return true;
      });

      rows.sort((a,b) => {
        if (sortV === 'model') return String(a.model||'').localeCompare(String(b.model||''));
        if (sortV === 'provider') return String(a.provider||'').localeCompare(String(b.provider||''));
        const la = a.latency_ms == null ? 1e18 : Number(a.latency_ms);
        const lb = b.latency_ms == null ? 1e18 : Number(b.latency_ms);
        return la - lb;
      });

      countEl.textContent = `${rows.length} / ${totalAll} shown`;
      tbody.innerHTML = '';
      for (const r of rows) {
        const tr = document.createElement('tr');
        const latency = r.latency_ms == null ? '' : Math.round(Number(r.latency_ms));
        const note = String(r.note||'');
        tr.innerHTML = `
          <td>${String(r.provider||'')}</td>
          <td><code>${String(r.model||'')}</code></td>
          <td>${statusBadge(r.status)}</td>
          <td>${accessBadge(r.access)}</td>
          <td>${String(r.tier||'')}</td>
          <td>${r.agentic_coding_candidate ? badge('Yes', 'ok') : badge('No', 'warn')}</td>
          <td class="lat">${latency ? latency + 'ms' : ''}</td>
          <td class="note" title="${note.replaceAll('"','&quot;')}">${note.slice(0, 220)}</td>
        `;
        tbody.appendChild(tr);
      }
    }

    async function loadSummary() {
      try {
        renderMetricSkeleton();
        const url = isStatic ? './hf_model_availability.json' : '/api/summary';
        setTableState('loading', 'Loading latest report…', 'Fetching data...');
        const r = await fetch(url, { cache: 'no-store' });
        if (!r.ok) throw new Error('no summary');
        DATA = await r.json();

        if (DATA.generated_at) {
          const genDate = new Date(DATA.generated_at);
          let genEl = document.getElementById('generatedAt');
          if (!genEl) {
            genEl = document.createElement('p');
            genEl.id = 'generatedAt';
            genEl.style.margin = '4px 0 0';
            genEl.style.color = 'var(--muted)';
            genEl.style.fontSize = '11px';
            document.querySelector('.overview-card .hd').appendChild(genEl);
          }
          genEl.textContent = 'Generated: ' + genDate.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
        }

        renderMetrics(DATA.summary || {});
        const providers = uniq((DATA.rows||[]).map(r => r.provider));
        const statuses = uniq((DATA.rows||[]).map(r => r.status));
        const access = uniq((DATA.rows||[]).map(r => r.access));
        providerEl.innerHTML = '<option value="">All</option>';
        statusSelEl.innerHTML = '<option value="">All</option>';
        accessEl.innerHTML = '<option value="">All</option>';
        providers.forEach(v => opt(providerEl, v));
        statuses.forEach(v => opt(statusSelEl, v));
        access.forEach(v => opt(accessEl, v));
        emptyStateEl.style.display = 'none';
        setTableState(null, '', '');
        renderTable();
      } catch (e) {
        if (!isStatic) {
          enableStaticMode();
          loadSummary();
          return;
        }
        DATA = null;
        metricsEl.innerHTML = '';
        tbody.innerHTML = '';
        countEl.textContent = '0 shown';
        emptyStateEl.style.display = 'block';
        if (isStatic) {
          setTableState('empty', 'No data loaded.', 'Could not fetch hf_model_availability.json.');
        } else {
          setTableState('empty', 'No data loaded.', 'Click “Run scan” to fetch the latest info.');
        }
      }
    }

    async function refreshStatus() {
      if (isStatic) return;
      try {
        const r = await fetch('/api/status', { cache: 'no-store' });
        if (r.status === 404) {
          enableStaticMode();
          return;
        }
        const j = await r.json();
        const msg = j.running ? 'running…' : (j.last_finished ? ('last finished: ' + j.last_finished) : 'idle');
        const exitText = (j.last_exit === null || j.last_exit === undefined) ? '' : (' • exit ' + j.last_exit);
        statusEl.innerHTML = `<b>${msg}</b><span style="color:rgba(255,255,255,.45)">${exitText}</span>`;
        btn.disabled = !!j.running;
        if (j.running) {
          setTableState('running', 'Scan in progress…', 'Results will refresh automatically when complete.');
        } else if (j.last_finished) {
          loadSummary();
        }
      } catch (e) {
        enableStaticMode();
      }
    }

    async function refreshSourceVersion() {
      if (isStatic) return;
      try {
        const r = await fetch('/api/source-version', { cache: 'no-store' });
        if (r.status === 404) {
          enableStaticMode();
          return;
        }
        if (!r.ok) return;
        const j = await r.json();
        if (j.version && j.version !== SOURCE_VERSION) {
          window.location.reload();
        }
      } catch (e) {
        // ignore
      }
    }

	    btn.addEventListener('click', async () => {
      btn.disabled = true;
      statusEl.innerHTML = '<b>starting…</b>';
      const res = await fetch('/api/run', { method: 'POST', cache: 'no-store' });
      if (!res.ok && res.status !== 202) {
        showToast('Could not start scan', `HTTP ${res.status}`);
      } else {
        showToast('Scan started', 'This can take a minute. Results refresh automatically.');
      }
      await refreshStatus();
	    });

	    [qEl, providerEl, statusSelEl, accessEl, agenticEl, sortEl].forEach(el => el.addEventListener('input', renderTable));
	    // Make arrow keys scroll the focused results area without taking over page scroll.
	    function isTypingTarget(el) {
	      if (!el) return false;
	      const tag = String(el.tagName || '').toLowerCase();
	      return tag === 'input' || tag === 'textarea' || tag === 'select' || el.isContentEditable;
	    }
	    function scrollResultsBy(delta) {
	      if (!tableWrapEl) return;
	      tableWrapEl.scrollTop += delta;
	    }
	    tableWrapEl && tableWrapEl.addEventListener('pointerdown', () => tableWrapEl.focus());
	    window.addEventListener('keydown', (e) => {
	      if (isTypingTarget(document.activeElement)) return;
	      if (!tableWrapEl) return;
	      if (document.activeElement !== tableWrapEl) return;
	      const key = e.key;
	      if (key === 'ArrowDown') { e.preventDefault(); scrollResultsBy(48); }
	      else if (key === 'ArrowUp') { e.preventDefault(); scrollResultsBy(-48); }
	      else if (key === 'PageDown') { e.preventDefault(); scrollResultsBy(tableWrapEl.clientHeight * 0.9); }
	      else if (key === 'PageUp') { e.preventDefault(); scrollResultsBy(-tableWrapEl.clientHeight * 0.9); }
	      else if (key === 'Home') { e.preventDefault(); tableWrapEl.scrollTop = 0; }
	      else if (key === 'End') { e.preventDefault(); tableWrapEl.scrollTop = tableWrapEl.scrollHeight; }
	    }, { passive: false });

	    loadSummary();
	    refreshStatus();
	    setInterval(() => { if (!isStatic) refreshStatus(); }, 2000);
	    setInterval(() => { if (!isStatic) refreshSourceVersion(); }, 1000);
  </script>
</body>
</html>
"""
    return html.replace("__FILES__", links).replace("__SOURCE_VERSION__", source_version()).encode("utf-8")

RUN_STATE = {
    "running": False,
    "last_started": None,
    "last_finished": None,
    "last_exit": None,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_scan(report_dir: Path) -> None:
    RUN_STATE["running"] = True
    RUN_STATE["last_started"] = utc_now()
    RUN_STATE["last_finished"] = None
    RUN_STATE["last_exit"] = None

    log_path = report_dir / "last_run.log"
    scanner_path = (Path(__file__).parent / "hf_model_scanner.py").resolve()
    cmd = [
        sys.executable,
        str(scanner_path),
        "--providers",
        "auto",
        "--output-dir",
        str(report_dir),
        "--route-provider",
        "auto",
        "--print-paths",
        "relative",
    ]
    try:
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=str(Path(__file__).parent))
            RUN_STATE["last_exit"] = proc.returncode
    except Exception:
        RUN_STATE["last_exit"] = 1
    finally:
        RUN_STATE["running"] = False
        RUN_STATE["last_finished"] = utc_now()


class Handler(BaseHTTPRequestHandler):
    report_dir: Path

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if url.path in {"/", "/index.html"}:
            body = build_index(self.report_dir)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if url.path == "/api/summary":
            report = self.report_dir / "hf_model_availability.json"
            if not report.exists():
                self.send_error(404, "hf_model_availability.json not found")
                return
            body = report.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if url.path == "/api/status":
            body = json.dumps(RUN_STATE).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if url.path == "/api/source-version":
            body = json.dumps({"version": source_version()}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if url.path.startswith("/files/"):
            name = url.path[len("/files/") :]
            if "/" in name or name.startswith(".") or ".." in name:
                self.send_error(400, "invalid file path")
                return
            target = (self.report_dir / name).resolve()
            if target.parent != self.report_dir.resolve() or not target.exists() or not target.is_file():
                self.send_error(404, "file not found")
                return

            content = target.read_bytes()
            ctype, _ = mimetypes.guess_type(target.name)
            self.send_response(200)
            self.send_header("Content-Type", (ctype or "application/octet-stream"))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404, "not found")

    def do_POST(self) -> None:
        url = urlparse(self.path)
        if url.path == "/api/run":
            if RUN_STATE.get("running"):
                body = json.dumps({"ok": False, "error": "already running"}).encode("utf-8")
                self.send_response(409)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            thread = threading.Thread(target=run_scan, args=(self.report_dir,), daemon=True)
            thread.start()
            body = json.dumps({"ok": True}).encode("utf-8")
            self.send_response(202)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "not found")

    def log_message(self, fmt: str, *args: object) -> None:
        # keep output quiet
        return


def watch_source_for_restart() -> None:
    source_path = Path(__file__)
    initial_version = source_version()
    while True:
        time.sleep(1)
        try:
            if str(source_path.stat().st_mtime_ns) != initial_version:
                print("web_report_server.py changed; restarting server...", flush=True)
                os.execv(sys.executable, [sys.executable, *sys.argv])
        except FileNotFoundError:
            continue


def main() -> int:
    args = parse_args()
    report_dir = (Path(__file__).parent / args.dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    if args.export:
        body = build_index(report_dir)
        sys.stdout.buffer.write(body)
        return 0

    Handler.report_dir = report_dir
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    if not args.no_auto_reload:
        threading.Thread(target=watch_source_for_restart, daemon=True).start()
    print(f"Serving {report_dir} on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
