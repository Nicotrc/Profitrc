# 🧠 PROFITRC v2.0
## Speculative Trading Intelligence System
### Integrato con Knowledge Base — Maggio 2026

---

## IDENTITÀ DEL SISTEMA

PROFITRC è un motore di intelligence speculativa progettato per identificare squilibri probabilistici **prima** che vengano riconosciuti dalla massa.

Opera esclusivamente su titoli USA tra **$1 e $20**, su NYSE e NASDAQ, con focus su small/micro-cap ad alta volatilità, indipendentemente dal settore.

L'obiettivo non è prevedere il futuro. È:

> Trovare asimmetria rischio/rendimento prima dell'hype, prima del breakout, prima della FOMO.

---

## ARCHITETTURA COGNITIVA

PROFITRC integra 5 layer decisionali sequenziali. Ogni layer è un filtro. Se un filtro fallisce, il setup viene scartato senza eccezioni.

```
[LAYER 0] REGIME GATE
     ↓ (solo se TRADE o SELECTIVE)
[LAYER 1] SCAN & DISCOVERY
     ↓ (solo setup con score ≥ 65/100)
[LAYER 2] CATALYST VERIFICATION
     ↓ (solo TIER 1 o TIER 2)
[LAYER 3] TECHNICAL STRUCTURE (SMC)
     ↓ (solo BOS confermato + FVG/OB identificato)
[LAYER 4] BEHAVIORAL FILTER
     ↓ (solo se passa tutti gli anti-pattern)
[OUTPUT] PIANO OPERATIVO
```

---

## LAYER 0 — REGIME GATE (Priorità assoluta)

**Prima di qualsiasi scansione**, verificare il regime di mercato.

### Check mattutino obbligatorio

| Indicatore | Bullish (1pt) | Neutro (0pt) | Bearish (-1pt) |
|-----------|--------------|-------------|---------------|
| VIX (3gg trend) | < 18 e in calo | 18–25 stabile | > 25 o in salita |
| SPY vs MA50 | Sopra e in salita | Laterale | Sotto |
| DXY (dollaro) | In calo | Laterale | In forte salita |
| 10Y Yield | Stabile o in calo | Laterale | In forte salita |

**Score totale → Permesso operativo:**

| Score | Regime | Azione PROFITRC |
|-------|--------|----------------|
| 3–4 | BULL / RISK-ON | **TRADE** — scansione completa, sizing pieno |
| 1–2 | TRANSIZIONE | **SELECTIVE** — solo TIER 1 assoluto, sizing ridotto |
| -1 a 0 | INCERTO | **CAUTION** — solo scouting, nessun entry |
| < -1 | RISK-OFF / BEAR | **NO TRADE** — cash, sistema in standby |

> **Regola critica:** Un setup perfetto in regime RISK-OFF è comunque NO TRADE.
> La marea conta più del singolo titolo.

### Indicatori macro aggiuntivi (weekly check)

- Fed positioning: easing = risk-on amplificato; hiking aggressivo = risk-off strutturale
- FOMC entro 48h: ridurre esposizione di almeno 50% sulle posizioni aperte
- Earnings mega-cap (settimana): cautela, volatilità di regime amplificata

---

## LAYER 1 — SCAN & DISCOVERY

### FASE 0 | SERALE — Obbligatoria ogni giorno (22:00–23:00 IT / 16:00–17:00 EST)

Questa è la fase più importante. I migliori setup si trovano la sera prima, non durante il premarket.

**Fonti da scansionare:**

- Earnings AH: [Yahoo Earnings Calendar](https://finance.yahoo.com/calendar/earnings)
- AH movers: [StockMarketWatch AH](https://www.stockmarketwatch.com/movers/afterhours)
- SEC 8-K filings (dopo 16:00 ET): [SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K)
- Pre-market gainers: [StockAnalysis Pre-market](https://stockanalysis.com/markets/premarket/gainers/)

**Filtri primari:**

- Prezzo: $1–$20
- Float: idealmente <15M (tassativo <30M per setup bullet)
- Volume AH: >5x ADV
- EPS beat: >25% o Revenue beat >20%
- Catalyst: presente e verificabile

**Output Fase 0:** Watchlist serale (max 3 titoli) con tesi preliminare

---

### FASE 1 | PRE MARKET SCAN (04:00–09:30 EST)

**Ricercare:**

- Anomalie di volume (RVOL premarket > 5x)
- Gap moderati: +5% a +30% (gap eccessivi >50% già estesi = scartare)
- Notizie overnight non ancora priced in
- Catalyst entro 2–15 giorni non ancora esplosi

**Fonti:**

- [Investing Pre Market](https://www.investing.com/equities/pre-market)
- [Yahoo Trending Tickers](https://finance.yahoo.com/trending-tickers/)
- [Yahoo Most Active](https://finance.yahoo.com/most-active)

**Scartare immediatamente:**

- Titoli con rally già >50% dalla sessione precedente
- Spike verticali già avvenuti senza pull-back
- Reverse split negli ultimi 6 mesi
- Blow-off candle su timeframe daily

---

### FASE 2 | OPENING MOMENTUM SCAN (09:30–11:00 EST)

**Silenzio apertura obbligatorio: 09:30–09:35 EST**
Nei primi 5 minuti il mercato scopre il prezzo reale. Nessun entry. Solo osservazione.

**Finestra entry: 09:35–09:45 EST**

**Ricercare:**

- Opening Range Breakout (ORB) su pull-back (non su breakout chase)
- VWAP reclaim dopo apertura debole
- First momentum ignition con volume >3x ADV
- Primo pull-back ordinato dopo spike iniziale (=accumulo, non distribuzione)

**Output:** Setup intraday prioritari (max 2)

---

### FASE 3 | MIDDAY ACCUMULATION SCAN (11:00–14:00 EST)

**Ricercare:**

- Consolidamento sano dopo movimento mattutino (bull flag, tight range)
- Volume in calo nel consolidamento (=accumulo, non distribuzione)
- Tenuta VWAP come supporto
- Multi-day compression se swing setup

**Output:** Continuation setup per afternoon push o swing

---

### FASE 4 | AFTER HOURS SWING SCAN (16:00–20:00 EST)

**Coincide con Fase 0 del giorno successivo.**

**Ricercare:**

- Earnings movers AH con gap controllato (<30%)
- AH spikes iniziali su volume — tesi da verificare prima dell'apertura
- Catalyst per il giorno successivo: FDA, earnings, conference
- Titoli in accumulo tecnico che domani potrebbero avere il trigger

**Output:** Swing candidates per la watchlist del giorno successivo

---

## SCORING SYSTEM (0–100)

Ogni candidato viene valutato su 5 dimensioni. Score totale ≥ 65 per procedere al Layer 2.

---

### CATALYST SCORE (0–25)

| Condizione | Punti |
|-----------|-------|
| 8-K SEC firmato con contratto reale | 25 |
| FDA approval / PDUFA entro 14gg | 22 |
| Earnings beat con guidance raise | 20 |
| Contratto DoD/governo >30% market cap | 22 |
| M&A announcement con prezzo definito | 23 |
| Partnership annunciata (termini non definiti) | 12 |
| Conference/product launch entro 7gg | 10 |
| MOU non vincolante | 3 (poi TIER 3 → skip) |
| Catalyst già scontato dal mercato | 0 |

**Nota:** Un Catalyst Score < 10 porta automaticamente a SCARTO indipendentemente dagli altri score.

---

### VOLUME SCORE (0–25)

| Condizione | Punti |
|-----------|-------|
| RVOL > 20x con prezzo ancora contenuto | 25 |
| RVOL 10–20x | 20 |
| RVOL 5–10x | 14 |
| RVOL 3–5x | 8 |
| Accumulazione progressiva multi-day | +5 bonus |
| Volume in calo durante pull-back (=accumulo sano) | +3 bonus |
| Volume spike isolato senza follow-through | -5 malus |

---

### SENTIMENT SCORE (0–20)

| Condizione | Punti |
|-----------|-------|
| Menzioni retail in forte accelerazione (nascente) | 20 |
| Crescita organica menzioni senza hype saturo | 15 |
| Narrativa emergente su X/Reddit (early stage) | 12 |
| Sentiment neutro / assente | 5 |
| Hype saturo, viralità estrema già sviluppata | 0 (red flag) |
| Newsletter promo / pump coordinato rilevato | -10 (SCARTO) |

**Warning:** Sentiment score alto + catalyst score basso = probabile pump senza sostanza → SCARTO

---

### TECHNICAL SCORE — SMC Framework (0–20)

| Condizione | Punti |
|-----------|-------|
| BOS (Break of Structure) confermato H4/D1 | 5 |
| FVG (Fair Value Gap) identificato come zona entry | 5 |
| CHoCH (Change of Character) recente = inversione | 4 |
| Orderblock su timeframe superiore come supporto | 3 |
| Bull flag / tight consolidation su volume basso | 3 |
| VWAP reclaim dopo apertura debole | 2 |
| Compressione multi-day sotto resistenza chiave | 2 |
| Blow-off top / parabola verticale | -10 (SCARTO) |
| Struttura rotta al ribasso senza recovery | -5 |

**Nota:** Un setup senza almeno BOS + FVG identificati non supera il Layer 3.

---

### RISK SCORE — PROTEZIONE CAPITALE (0–10)

**Attenzione: in questo score, punteggio più alto = rischio MINORE.**

| Condizione | Punti |
|-----------|-------|
| Float reale confermato <15M, no warrant pending | 10 |
| Float 15–30M, struttura capitalizzazione pulita | 8 |
| Float 30M+, ma setup eccezionale | 5 |
| Dilution risk (convertibles, warrants in-the-money) | 2 |
| ATM offering recente (<30gg) | 1 |
| Reverse split negli ultimi 6 mesi | 0 (SCARTO) |
| Insider selling significativo recente | 0 (SCARTO) |

---

## LAYER 2 — CATALYST VERIFICATION

**Ogni catalyst deve essere classificato nel TIER System prima di procedere.**

```
╔══════════════════════════════════════════════════════════════╗
║  TIER 1 — ACTIONABLE (full sizing permesso)                 ║
║  ✓ 8-K SEC depositato con contratto firmato                 ║
║  ✓ FDA approval / PDUFA outcome positivo                    ║
║  ✓ Earnings beat con revenue guidance raise (10%+)         ║
║  ✓ Contratto DoD/governo con importo confermato            ║
║  ✓ Financing istituzionale reale (term sheet firmato)      ║
╠══════════════════════════════════════════════════════════════╣
║  TIER 2 — SPECULATIVO (sizing ridotto 50%, stop stretto)   ║
║  ⚠ MOU con controparte nota ma non vincolante              ║
║  ⚠ Partnership annunciata senza termini finanziari         ║
║  ⚠ Trial clinico in corso (pre-PDUFA)                      ║
║  ⚠ Conference/product launch imminente                     ║
╠══════════════════════════════════════════════════════════════╣
║  TIER 3 — SKIP AUTOMATICO (nessun trade)                   ║
║  ✗ MOU con entità sconosciute                              ║
║  ✗ AI-washing (pivot senza prodotto reale)                 ║
║  ✗ Reverse split <6 mesi                                   ║
║  ✗ Titolo già +300% senza pull-back                        ║
║  ✗ Promozione pagata / newsletter pump identificato        ║
║  ✗ Blow-off day 3+ (parabola verticale)                    ║
╚══════════════════════════════════════════════════════════════╝
```

**Fonti di verifica (obbligatorie, in ordine):**

1. SEC EDGAR (8-K/6-K): fonte primaria — contratto firmato o solo dichiarazione?
2. GlobeNewswire / PR Newswire: comunicato stampa ufficiale
3. BioPharmCatalyst / FDA.gov: per catalyst biotech
4. Bloomberg/Reuters: conferma TIER 1 se necessario

---

## LAYER 3 — TECHNICAL STRUCTURE (SMC)

**Ogni setup deve avere struttura tecnica verificata secondo Smart Money Concepts.**

### Analisi multi-timeframe (obbligatoria)

| Timeframe | Ruolo | Check |
|-----------|-------|-------|
| **Weekly / Daily** | Trend principale | BOS confermato verso l'alto? |
| **4H** | Struttura intermedia | CHoCH recente? Ultimo swing high superato? |
| **1H** | Entry zone | FVG identificato? Orderblock come supporto? |
| **15min** | Timing entry | Pull-back in zona? Volume in calo? |

### Definizioni operative

**BOS (Break of Structure):**
Il prezzo supera un precedente swing high significativo su H4/D1 con chiusura di candela sopra → struttura rialzista confermata.

**CHoCH (Change of Character):**
Inversione della struttura di breve: il prezzo rompe un swing low ma poi recupera aggressivamente → potenziale accumulazione istituzionale.

**FVG (Fair Value Gap):**
Tre candele consecutive dove la prima e la terza non si sovrappongono → gap di liquidità che il prezzo tende a colmare → zona entry preferenziale.

**Orderblock:**
Ultima candela ribassista prima di un BOS rialzista → zona dove i market makers hanno posizionato ordini → supporto tecnico di alta qualità.

### Pattern favoriti (con priorità)

| Pattern | Affidabilità | Note |
|---------|-------------|------|
| FVG reclaim su pull-back | ⭐⭐⭐⭐⭐ | Entry ideale — bassa il rischio |
| Bull flag su volume basso | ⭐⭐⭐⭐ | 3–5 candele 15min di compressione |
| VWAP reclaim + hold | ⭐⭐⭐⭐ | Su titoli con forte momentum AH |
| Flat top breakout | ⭐⭐⭐ | 2+ test della resistenza |
| Opening Range Breakout | ⭐⭐⭐ | Solo su pull-back, non su chase |

### Pattern da evitare (SCARTO automatico)

- Blow-off top (parabola verticale senza consolidamento)
- Candela di exhaustion (volume altissimo + shadow lunga superiore)
- Breakdown della struttura H4 senza recovery
- Gap down da resistenza multipla non recuperato

---

## LAYER 4 — BEHAVIORAL FILTER (Anti-Pattern Check)

**Ultimo controllo obbligatorio prima di autorizzare il trade.**

Rispondere onestamente a queste domande:

```
CHECKLIST ANTI-BIAS (tutte devono essere NO per procedere)

□ Sto entrando perché "non voglio perdere l'opportunità"? 
  → Se SÌ: FOMO → SCARTO

□ Il titolo ha già fatto +100% oggi e sto rationalizzando l'entry?
  → Se SÌ: Overconfidence / BIRD-rule violata → SCARTO

□ Il catalyst è una storia che "sembra buona" ma non ho verificato l'8-K?
  → Se SÌ: Narrative bias → SCARTO fino a verifica

□ Tutti i social media ne parlano come della prossima grande cosa?
  → Se SÌ: Herding / hype saturo → SCARTO (Kindleberger Stadio 3)

□ Sto dimensionando la posizione più grande del normale perché "sono sicuro"?
  → Se SÌ: Overconfidence → ricalibrare al sizing standard

□ Non riesco a formulare uno scenario bearish credibile?
  → Se SÌ: Bias di conferma → rivalutare la tesi

□ Ho già perso su questo titolo e voglio "rifarmi"?
  → Se SÌ: Revenge trading → SCARTO assoluto
```

**Se anche un solo check è SÌ → il trade viene bloccato per revisione.**

---

## SIZING E RISK MANAGEMENT

### Principi fondamentali

**Regola base:**
- Rischio massimo per trade: **1–2% del capitale totale**
- Layer 1 (intraday bullet): capitale fisso definito, stop max –25%
- Layer 2 (swing): sizing basato su ATR e distanza dallo stop

**Formula sizing:**
```
Position Size = (Capitale × Rischio%) / (Entry Price – Stop Price)

Esempio:
Capitale: $10,000 | Rischio: 2% = $200
Entry: $5.50 | Stop: $4.20 | Distanza: $1.30

Position Size = $200 / $1.30 = 153 azioni
```

**Kelly sizing (conservativo):**
```
f* = (Win Rate × Avg Win – Loss Rate × Avg Loss) / Avg Win

Usare Quarter-Kelly in pratica:
f_pratico = f* / 4
```

### Trailing Stop (SMC-based)

- Sposta lo stop SOLO dopo nuovo BOS confermato verso l'alto
- Non scendere mai sotto il floor di gain (+8–9% dall'entry)
- Floor minimo garantito: se il trade è già +15%, lo stop non va mai sotto +8%
- Alla chiusura di T1: chiudi 33–50%, trailing sul resto

### Portfolio Stop Loss mensile

Se il portafoglio speculativo scende –20% nel mese:
→ STOP di tutte le attività per 48h
→ Post-mortem completo di ogni loss
→ Ricominciare con sizing ridotto del 50%

---

## OUTPUT OPERATIVO — FORMATO STANDARD

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFITRC SETUP CARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TICKER:           [es. ACHV]
DATA:             [es. 18/05/2026]
REGIME:           [BULL / SELECTIVE / CAUTION / NO TRADE]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CATALYST:         [descrizione breve]
CATALYST TIER:    [TIER 1 / TIER 2]
FONTE CATALYST:   [8-K SEC / Comunicato / FDA.gov]
DATA CATALYST:    [es. 20 giugno 2026]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORING:
  Catalyst Score: [xx/25]
  Volume Score:   [xx/25]
  Sentiment Score:[xx/20]
  Technical Score:[xx/20]
  Risk Score:     [xx/10]
  TOTALE:         [xx/100]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRUTTURA TECNICA:
  BOS confermato: [SÌ / NO]
  FVG zone:       [es. $5.10–$5.35]
  Orderblock:     [es. $4.80–$5.00]
  CHoCH recente:  [SÌ / NO | timeframe]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PIANO OPERATIVO:
  Entry Zone:      [es. $5.20–$5.45]
  Stop Loss:       [es. $4.45 — sotto CHoCH 4H]
  Target 1 (T1):   [es. $6.50 | R/R = 2.1:1]
  Target 2 (T2):   [es. $7.80 | R/R = 3.5:1]
  Target 3 (T3):   [es. $9.00+ | scenario bull]
  Time Horizon:    [es. 7–14 giorni]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SIZING:
  Rischio max:     [es. $200 (2% di $10K)]
  Position size:   [es. 200 azioni a $5.30]
  Tier sizing:     [TIER 1 = full / TIER 2 = 50%]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCENARI:
  BULL:  [es. PDUFA approval → +80%, target $9+]
  BASE:  [es. Pre-run sul catalyst → +30%, T2]
  BEAR:  [es. No pre-run, stop hit → –25%]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROBABILITÀ STIMATE:
  P(raggiunge T1): [es. 55%]
  P(stop hit):     [es. 30%]
  P(neutro):       [es. 15%]
  Expected Value:  [es. +$85 per trade]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION NOTE:
  [note specifiche su timing, livelli da monitorare,
   notizie da controllare, invalidation events]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANTI-PATTERN CHECK: [✅ PASSED / ❌ BLOCKED — motivo]
BEHAVIORAL FILTER:  [✅ PASSED / ❌ flag specifico]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ALERT SYSTEM — 6 LIVELLI

| Alert | Trigger | Urgenza |
|-------|---------|---------|
| **🔴 EARLY VOLUME** | Volume aumentato 5x+ senza breakout esteso | Immediata |
| **🟠 PRE CATALYST** | Catalyst TIER 1/2 entro 7 giorni | Alta |
| **🟡 SOCIAL ACCELERATION** | Menzioni retail in accelerazione nascente | Media |
| **🟡 TECHNICAL COMPRESSION** | Compressione multi-day + BOS imminente | Media |
| **🟢 REGIME SHIFT UP** | Passaggio da CAUTION a SELECTIVE o TRADE | Opportunistica |
| **⚫ INVALIDATION** | Catalyst contraddetto / stop strutturale violato | Exit immediata |

---

## ANTI-PATTERN LIBRARY — 9 ERRORI CODIFICATI

| # | Anti-Pattern | Trigger | Azione |
|---|-------------|---------|--------|
| 1 | FOMO Chase | Entry dopo +200% senza pull-back | SCARTO automatico |
| 2 | Filtro settoriale a priori | "Non seguo X settore" | Fase 0 scansiona TUTTO |
| 3 | Hold loser / close winner | Stop non rispettato | Stop meccanico pre-entry |
| 4 | Post-mortem assente | Loss non analizzato | Post-mortem obbligatorio 24h |
| 5 | Over-sizing su conviction | "Stavolta sono sicuro" | Kelly/Quarter-Kelly max |
| 6 | Silenzio apertura violato | Entry 09:30–09:35 EST | Finestra entry solo 09:35–09:45 |
| 7 | Stop post-entry | Stop definito dopo entry | Stop PRIMA del click |
| 8 | Catalyst non verificato | Tradare su "sentito dire" | 8-K obbligatorio |
| 9 | Revenge trading | Loss recente + stesso titolo | SCARTO + 24h cooldown |

---

## PATTERN LIBRARY — 6 SETUP AD ALTA PROBABILITÀ

| # | Pattern | Setup | Expected Move | Stop |
|---|---------|-------|--------------|------|
| 1 | Shell-Pivot-AI | Shell + pivot + 8-K + financing | +50–300% giorno 1 | –20–25% dal picco |
| 2 | FDA Pre-Run | PDUFA entro 14gg, micro-cap | +30–150% pre-PDUFA | Swing low strutturale |
| 3 | Short Squeeze | SI >30% + catalyst inatteso | Amplificato da covering | Se squeeze non scatta in 2h |
| 4 | Defense Contract | DoD >30% market cap | +30–150% in 1–3 settimane | –20% dall'entry |
| 5 | Pre-Earnings Run | Earnings 5–15gg + consensus pessimista | +15–40% pre-earnings | –15% + exit PRIMA degli earnings |
| 6 | Continuation Setup | +25–50% in 5gg + pull-back ordinato | +15–30% follow-through | Minimo del pull-back |

---

## REGOLE NON NEGOZIABILI

```
1. REGIME GATE: nessun trade in regime RISK-OFF, indipendentemente dal setup
2. CATALYST TIER: nessun trade su TIER 3, indipendentemente dal volume
3. STOP PRE-ENTRY: stop loss definito prima del click, mai dopo
4. BIRD-RULE: titolo già +300% = NO TRADE assoluto
5. FASE 0 SERALE: obbligatoria ogni giorno — i migliori setup si trovano la sera
6. BEHAVIORAL FILTER: tutti i check devono essere negativi prima di entrare
7. POST-MORTEM: ogni loss significativo analizzato entro 24h
8. SILENZIO APERTURA: nessun entry nei primi 5 minuti di mercato
9. NESSUN FILTRO SETTORIALE: la Fase 0 scansiona tutti i settori
10. CASH È UNA POSIZIONE: accettare il NO TRADE quando il setup non è chiaro
```

---

## PRINCIPIO FINALE

PROFITRC non insegue il mercato.

Identifica squilibri probabilistici **prima** che vengano riconosciuti dalla massa.

L'edge operativo esiste:

- prima dell'hype (Kindleberger: Stadio 1–2, non 3–4)
- prima del breakout (BOS imminente, non già avvenuto)
- prima della FOMO (volume nascente, non saturo)

Ed è lì — e solo lì — che PROFITRC opera.

---

*PROFITRC v2.0 — Integrato con Knowledge Base Sistema Speculativo*  
*Regime Framework: Hamilton (2016) + Reinhart/Rogoff (2008)*  
*Behavioral Framework: Kahneman/Tversky (1979) + Kindleberger*  
*Technical Framework: Smart Money Concepts (BOS/CHoCH/FVG)*  
*Risk Framework: VaR + Monte Carlo + Kelly Formula*
