# PROFITRC v2 — Modifiche applicate (maggio 2026)

## Problemi risolti

### 1. ACHV / IBRX — errore HTTP 500 su Analyze
**Causa:** `stop_loss` dalla struttura tecnica poteva essere **sopra** l'entry (setup long invalido) → `ValueError` in `RiskManager`.

**Fix:** `RiskManager.normalize_long_levels()` + uso in `api/server.py` e `main.py`.

### 2. Scanner fasi 1–3 vuoti
**Causa:** scraping HTML (StockAnalysis, Yahoo) spesso fallisce; Yahoo Screener API può rispondere 429.

**Fix:**
- Fallback `fetch_yahoo_screener()` (JSON API)
- Fallback universale `fetch_earnings_movers()` se nessun ticker
- Feed SEC via `requests` (TLS più affidabile)

### 3. Scan API in NO_TRADE
**Fix:** parametro `bypass_regime=true`; UI checkbox "Bypass NO_TRADE".
- Lo scan restituisce **tutti** i ticker analizzati (anche SKIP), non solo PROCEED/REVIEW.

### 4. Doppia chiamata SEC EDGAR
**Fix:** `calculate_risk_score(..., catalyst_data=)` riusa `sec_filing` già scaricato.

### 5. SEC CIK errato
**Fix:** risoluzione ticker → CIK tramite `company_tickers.json` SEC.

## File modificati

| File | Modifica |
|------|----------|
| `modules/risk_manager.py` | `normalize_long_levels()` |
| `modules/scorer.py` | `catalyst_data` in risk score |
| `modules/catalyst_verifier.py` | CIK map + feed via requests |
| `modules/scanner.py` | Screener Yahoo + fallback earnings |
| `modules/data_cache.py` | Gestione `None` su history |
| `api/server.py` | Scan/analyze robusti |
| `main.py` | Entry/stop normalizzati |
| `frontend/.../ScanPanel.tsx` | Bypass NO_TRADE + conteggi |
| `deploy-local.sh` | Script Docker locale (nuovo) |

## Deploy locale (Docker)

```bash
cd profitrc
chmod +x deploy-local.sh
./deploy-local.sh          # build + avvio
./deploy-local.sh --rebuild   # rebuild completo
./deploy-local.sh --logs      # segue i log
```

Apri: **http://localhost:8080**

### Test manuali

```bash
# Singolo ticker (non dipende dal regime)
curl -s http://localhost:8080/api/analyze/ACHV | python3 -m json.tool | head -40

# Scan con bypass NO_TRADE
curl -s -X POST 'http://localhost:8080/api/scan/0?bypass_regime=true' \
  -H 'Content-Type: application/json' \
  -d '{"capital":10000}' | python3 -m json.tool | head -60
```

## Note operative

- **NO_TRADE** con score -3 è ancora il comportamento corretto del Regime Gate: in standby non si aprono nuove operazioni.
- Per **vedere** setup in quelle condizioni: Analyze singolo ticker oppure scan con bypass.
- I ticker con verdict **SKIP** compaiono nello scan (utili per diagnostica); solo PROCEED/REVIEW contano in `passed_count`.
