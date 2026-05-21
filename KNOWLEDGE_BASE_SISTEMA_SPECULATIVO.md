# 📚 KNOWLEDGE BASE — SISTEMA DI INVESTIMENTO SPECULATIVO
> Versione 1.0 — Maggio 2026  
> Documento portabile: sintesi operativa di 29 fonti accademiche e istituzionali  
> Autore sistema: Nicola | Architettura: Multi-layer speculativo (Layer 1 intraday + Layer 2 swing)

---

## INDICE

1. [MAPPA COGNITIVA DEL SISTEMA](#1-mappa-cognitiva)
2. [MODULO MACRO — Regimi, Crisi, Liquidità](#2-modulo-macro)
3. [MODULO BEHAVIORAL — Bias, Psicologia, Anti-errori](#3-modulo-behavioral)
4. [MODULO RISK — VaR, Monte Carlo, Stress Test](#4-modulo-risk)
5. [MODULO PORTFOLIO — Costruzione, Allocazione, Fattori](#5-modulo-portfolio)
6. [MODULO HEDGE FUND — Strategie, Alpha, Replica](#6-modulo-hedge-fund)
7. [MODULO QUANTITATIVE — Sistemi, Backtesting, Execution](#7-modulo-quantitative)
8. [FRAMEWORK OPERATIVO INTEGRATO](#8-framework-operativo)
9. [REGOLE NON NEGOZIABILI](#9-regole-non-negoziabili)
10. [FONTI E CREDENZIALI](#10-fonti)

---

## 1. MAPPA COGNITIVA

Il sistema integra 7 domini di conoscenza in una pipeline decisionale sequenziale:

```
INPUT MERCATO
     │
     ▼
[MACRO REGIME DETECTOR] ──── Hamilton (2016) + Reinhart/Rogoff (2008)
     │                        → Permesso operativo: TRADE / NO TRADE / SELECTIVE
     ▼
[BEHAVIORAL FILTER] ──────── Kahneman/Tversky (1979) + Giancola (2020)
     │                        → Rimozione bias: FOMO, overconfidence, herding
     ▼
[TECHNICAL STRUCTURE] ────── KoMagamebook (SMC) + MIT 15.401
     │                        → BOS, CHoCH, FVG, Fibonacci
     ▼
[CATALYST VALIDATOR] ─────── Event-driven framework
     │                        → TIER 1/2/3 classification
     ▼
[MOMENTUM & FLOW] ─────────── Fama/French (1993) + Ernie Chan (2009)
     │                        → Volume ratio, size factor, momentum factor
     ▼
[RISK SIZING] ─────────────── VaR (Damodaran) + Monte Carlo + Ryu stress test
     │                        → Position size, stop loss, drawdown max
     ▼
[EXECUTION] ───────────────── Kelly formula + Vanguard PCF
     │                        → Entry timing, gestione posizione, exit
     ▼
[CRITICAL REVIEW] ─────────── Kindleberger + Limit of Arbitrage
                               → Anti-pattern check, annullamento se fallisce
```

**Principio guida unificante:** I mercati non sono deterministici. Il vantaggio deriva dalla convergenza di segnali multipli, da una gestione rigorosa del rischio e dalla capacità di restare in cash quando nessun setup supera tutti i filtri.

---

## 2. MODULO MACRO — Regimi, Crisi, Liquidità

### 2.1 MACROECONOMIC REGIMES AND REGIME SHIFTS
**Fonte:** James D. Hamilton — NBER Working Paper 21863, January 2016  
**Istituzione:** University of California San Diego / NBER

#### Concetto chiave: Regime come stato latente
Le serie temporali economiche non seguono un unico processo lineare — presentano **rotture strutturali** associate a recessioni, panic finanziari e crisi valutarie. Il cambiamento di regime è un fenomeno non lineare: non è prevedibile con metodi lineari standard.

#### Modello di Markov a stati nascosti (Hamilton 1989)
Il modello fondamentale di Hamilton assume che l'economia si trovi in uno di `N` stati latenti `s_t` non direttamente osservabili:
- **Stato 1:** espansione (crescita positiva, bassa volatilità)
- **Stato 2:** recessione / contrazione (crescita negativa, alta volatilità)

La transizione tra stati è governata da una matrice di probabilità:
```
P(s_t = j | s_{t-1} = i) = p_ij
```

**Implicazione operativa:**  
Non basta guardare i dati correnti — occorre stimare *in quale regime* ci si trova. La probabilità di essere in regime di espansione è il filtro che abilita o disabilita l'operatività.

#### 4 Regimi identificabili nei mercati finanziari
| Regime | Caratteristiche | Permesso operativo |
|--------|----------------|-------------------|
| **BULL / Risk-On** | VIX basso, rendimenti positivi, spread ridotti, liquidità abbondante | TRADE — massima esposizione |
| **BEAR / Risk-Off** | VIX alto, flight to quality, dollaro forte, spread allargati | NO TRADE — cash o short |
| **TRANSIZIONE** | Segnali misti, tipping points, rotture strutturali | SELECTIVE — solo TIER 1 |
| **HIGH VOLATILITY** | Regime indeterminato, picchi VIX, correlazioni abnormi | NO TRADE — attendere chiarimento |

#### Tipping Points e crisi finanziarie (Sezione 3.5)
- I mercati finanziari possono avere **equilibri multipli** — transizioni rapide e discontinue tra stati stabili
- I tipping points sono raramente prevedibili prima che accadano, ma **riconoscibili nei segnali precursori**
- Segnali precursori di regime shift: inversione curva dei rendimenti, allargamento spread creditizi, crollo dei volumi di fiducia, aumento correlazioni cross-asset

#### Applicazione pratica al sistema
```
MORNING CHECK (quotidiano):
□ VIX trend (3 days): in calo = risk-on confermato
□ SPY/QQQ price action: sopra MA50 = trend up
□ DXY direction: in calo = liquidity supportive
□ 10Y yield: stabile o in calo = growth narrative
→ Se 3/4 positivi: TRADE autorizzato
→ Se 2/4 positivi: SELECTIVE (solo TIER 1)
→ Se 1/4 o meno: NO TRADE
```

---

### 2.2 THIS TIME IS DIFFERENT: EIGHT CENTURIES OF FINANCIAL CRISES
**Fonte:** Carmen M. Reinhart & Kenneth S. Rogoff — NBER Working Paper 13882, March 2008  
**Copertura:** 66 paesi, 800 anni di dati, 8 tipologie di crisi

#### La sindrome "This Time Is Different"
**Definizione:** La tendenza sistematica di investitori e policymaker a credere che le circostanze attuali siano fondamentalmente diverse dal passato — giustificando così valutazioni e debiti insostenibili.

**Manifestazioni ricorrenti:**
- "I fondamentali sono solidi" (prima di ogni crisi finanziaria)
- "La tecnologia ha cambiato i paradigmi" (bolla dot-com 2000)
- "Il settore immobiliare non scende mai" (2006-2007)
- "L'AI giustifica qualsiasi multiplo" (rischio attuale)

#### Anatomia universale delle crisi (pattern storico)
```
FASE 1 — DISPLACEMENT
Evento esogeno che cambia le aspettative economiche:
→ Innovazione tecnologica, liberalizzazione finanziaria, scoperta risorse

FASE 2 — BOOM / OVERTRADING
→ Prezzi in salita, leva crescente, euforia diffusa
→ Nuovi strumenti finanziari, nuovi partecipanti
→ "Gli scettici hanno torto"

FASE 3 — DISTRESS
→ Dubbi crescenti sulla sostenibilità
→ Istituzioni in difficoltà, swindling rivelato
→ Liquidità in calo, interesse a vendere cresce

FASE 4 — REVULSION / PANIC
→ Vendita precipitosa, corsa agli sportelli
→ Crollo prezzi, crisi creditizia
→ Lender of last resort richiesto

FASE 5 — AFTERMATH
→ Normalizzazione lenta (tipicamente 7-10 anni per recovery completo)
→ Regolazione aumentata, avversione al rischio strutturale
```

#### Key finding empirici (800 anni di dati)
- **Serial default** è quasi universale nei mercati emergenti
- Le grandi crisi sono tipicamente separate da **decenni**, creando l'illusione di eccezionalità
- Crisi bancarie + crisi valutarie si accompagnano frequentemente al default sovrano
- L'impatto medio sull'output delle crisi bancarie severe: **-9% del PIL, durata 2 anni**
- Mercati emergenti che "escono" dal serial default ci mettono in media **25-30 anni**

#### Applicazione al sistema speculativo
**Anti-FOMO framework:** Quando un settore ha già prodotto rendimenti >300% in breve tempo, applicare il test "This Time Is Different":
1. Ci sono precedenti storici di questo tipo di movimento?
2. Il movimento è sostenuto da cash flow reali o da aspettative auto-referenziali?
3. Il consensus narrativo è unanimemente bullish?

→ Se le risposte sono 1=sì, 2=aspettative, 3=sì → **ATTENZIONE MASSIMA / RIDURRE ESPOSIZIONE**

---

### 2.3 MANIAS, PANICS, AND CRASHES
**Fonte:** Charles P. Kindleberger — Classic work on financial crises (5th edition referenced)  
**Framework base:** Modello di Hyman Minsky adattato

#### Il modello Minsky-Kindleberger del ciclo speculativo

```
STADIO 1: DISPLACEMENT
→ Evento esogeno che modifica le opportunità di profitto atteso
→ Esempi: deregolamentazione, innovazione, fine di una guerra
→ "New opportunities emerge that seem genuinely different"

STADIO 2: BOOM / MANIA
→ Credit expansion alimenta la domanda
→ Prezzi salgono → aspettative di salita ulteriore → nuovi entranti
→ Overtrading: "il prezzo di oggi giustifica il prezzo di domani"
→ Feedback loop positivo auto-alimentante

STADIO 3: EUPHORIA / OVERTRADING
→ Speculatori "comprano per rivendere", non per il valore intrinseco
→ Nuovi strumenti finanziari creati per soddisfare la domanda
→ Leverage massimo, prudenza abbandonata
→ "Irrational exuberance" (Greenspan, 1996: NYSE a 6,400 → poi salì a 11,000)

STADIO 4: DISTRESS
→ Insiders iniziano a vendere
→ Prime rivelazioni di frodi (swindles emerge when credit tightens)
→ Liquidità in calo, bid-ask spread allargano
→ "Smart money" esce silenziosamente

STADIO 5: REVULSION
→ Inversione rapida: da comprare ad ogni calo a vendere ad ogni rimbalzo
→ Panico
→ Rush to convert illiquid assets to money

STADIO 6: CRASH / LENDER OF LAST RESORT
→ Crollo prezzi
→ Credit crunch
→ Intervento banca centrale o governo
```

#### Objects of Speculation (lista storica Kindleberger)
- Commodity exports e imports
- Urban real estate
- Stocks & bonds (domestic e foreign)
- New financial instruments
- Conglomerates, glamour stocks

**Pattern moderno applicabile:** AI stocks, crypto, SPAC, meme stocks — tutti seguono gli stessi stadi.

#### Regola operativa critica derivata
**BIRD-type rule:** Quando un titolo ha già prodotto +300% in un singolo giorno o settimana → il sistema è in Stadio 3-4 → **NO TRADE assoluto**. Il momento profittevole è prima, non dopo l'esplosione.

**Early detection indicators:**
- Volumi >10x la media su notizie non eccezionali
- Retail participation improvvisa (social media, forum)
- Analisti che alzano target price dopo il movimento
- CEO che vende azioni "per ragioni personali"

---

### 2.4 GLOBAL TRANSMISSION OF US MONETARY POLICIES
**Fonte:** Working Paper — analisi empirica trasmissione politiche monetarie USA  
**Rilevanza:** Capire dove fluisce la liquidità

#### Meccanismo di trasmissione
Le politiche monetarie della Federal Reserve si trasmettono globalmente attraverso 3 canali:

**Canale 1 — Interest Rate Channel**
- Fed funds rate ↑ → dollaro si apprezza → capitali rientrano negli USA
- Emerging markets subiscono outflow → crisi valutarie possibili
- Risk-off globale

**Canale 2 — Risk Appetite / Portfolio Balance Channel**
- Fed easing → tassi reali negativi → "search for yield"
- Capitali si spostano verso asset rischiosi (EM, small cap, high yield)
- Liquidity flood → Risk-on strutturale

**Canale 3 — Commodity Price Channel**
- Dollaro forte = commodity in dollari più care → deflationary
- Dollaro debole = commodity più care in USD ma boost per produttori
- Impatto asimmetrico su energy, metals, agricultural

#### Framework pratico per il sistema

| Regime Fed | Impatto mercati | Azione sistema |
|-----------|----------------|----------------|
| **Easing / Pivot** | Risk-on, small cap outperform, liquidity flood | TRADE — massima aggressività |
| **Pause** | Selettivo, quality bias, earnings drive | SELECTIVE — solo catalyst TIER 1 |
| **Hiking aggressivo** | Risk-off, flight to quality, VIX alto | NO TRADE / ridurre esposizione |
| **QE restart** | Explosive risk-on, tutti gli asset salgono | TRADE — window of opportunity |

**Check FOMC pre-decisione:** riduzione esposizione 48h prima dell'annuncio se posizioni aperte significative.

---

### 2.5 BEHAVIORAL MODEL OF THE DOT-COM BUBBLE AND CRASH
**Fonte:** Paper accademico — modello comportamentale bolla tech 1995-2002

#### Il ciclo dot-com come case study definitivo

**Fase 1 (1995-1998): Genuine Innovation**
- Internet era davvero rivoluzionario
- Prime IPO di aziende con modelli di business reali
- P/E multipli alti ma "giustificabili" con narrative di crescita

**Fase 2 (1998-2000): Narrative Hijacking**
- Qualsiasi azienda con ".com" nel nome vedeva il titolo triplicare
- Profitabilità irrilevante — "eyeballs" e "growth at any cost"
- Venture capital in competizione per investire a qualsiasi valutazione
- Retail investors FOMO al massimo

**Fase 3 (2000-2002): Crash e aftermath**
- NASDAQ da 5,048 (marzo 2000) a 1,114 (ottobre 2002): -78%
- Aziende "reali" scesero del 70-90% nonostante fondamentali solidi
- Correlazioni impazzite: tutto scese insieme

#### Pattern applicabile all'AI hype attuale
Distinguere tra:
- **AI Infrastructure reale** (chip, data center, cloud) = value reale, meno speculativo
- **AI Applications** (SaaS che aggiungono "AI" al pitch) = maggior rischio di narrative collapse
- **AI washing** (aziende che cambiano nome o pivot senza sostanza) = TIER 3 → SKIP

**Test pratico:** L'azienda ha ricavi/profitti che crescono a causa dell'AI, o solo la valutazione?

---

## 3. MODULO BEHAVIORAL — Bias, Psicologia, Anti-errori

### 3.1 PROSPECT THEORY
**Fonte:** Daniel Kahneman & Amos Tversky — *Journal of Econometrics*, 1979  
**Impatto:** Premio Nobel Economia 2002 (Kahneman)

#### La funzione del valore
Kahneman e Tversky dimostrarono che le persone non valutano gli outcomes in termini assoluti ma **relativi a un punto di riferimento**:

```
v(x) = { x^α                    se x ≥ 0 (guadagni)
        { -λ(-x)^β               se x < 0 (perdite)

Dove:
- α, β ≈ 0.88 (concavità per guadagni, convessità per perdite)
- λ ≈ 2.25 (loss aversion coefficient)
```

**Interpretazione:** Una perdita di $100 causa circa 2.25 volte il dolore psicologico del piacere prodotto da un guadagno di $100.

#### Distorsioni probabilistiche (Weighting Function)
Le persone **sovrappesano** le probabilità basse e **sottopesano** quelle medie-alte:
- Probabilità 1% viene percepita come ~5% (overweighting di eventi rari)
- Probabilità 99% viene percepita come ~95%

**Implicazioni dirette per il trader:**

| Bias | Manifestazione in trading | Contromisura |
|------|--------------------------|--------------|
| **Loss aversion** | Tenere losers troppo a lungo, vendere winners troppo presto | Stop loss meccanico PRE-entry |
| **Overweighting rare events** | Pagare troppo per tail hedges / FOMO su low-probability moonshots | Probabilità calibrate, non intuitive |
| **Reference point** | "Ho perso dal massimo, quindi devo recuperare" | Ogni giorno è un nuovo entry — ignora il costo storico |
| **Disposition effect** | Realizzo gains prematuro, hold losses | Trailing stop invece di target fisso |

#### Framing Effect
Come viene presentato un trade influenza la decisione **indipendentemente dai numeri**:
- "90% di probabilità di guadagnare" vs "10% di perdita" → stessa realtà, percezione diversa
- **Applicazione:** Formulare sempre i trade in termini di R/R, non di "potenziale guadagno"

#### Il Pain of Regret
Le persone fanno scelte per minimizzare il rimpianto anticipato, non per massimizzare il valore atteso:
- **Omission bias:** è più doloroso fare qualcosa di sbagliato che non fare qualcosa di giusto
- **Manifestazione in trading:** paura di entrare > paura di perdere l'opportunità → paralisi
- **Contromisura:** sistema di regole che forza l'azione quando i criteri sono soddisfatti

---

### 3.2 OVERCONFIDENCE IN FINANCIAL MARKETS
**Fonte:** Paper accademico sull'overconfidence — finanza comportamentale

#### 3 forme di overconfidence documentate

**1. Overconfidence sulla precisione (Overprecision)**
- Intervalli di confidenza sistematicamente troppo stretti
- Un trader overconfident dice "BTC arriverà a $120K" invece di "BTC ha il 60% di probabilità di essere tra $90K e $150K"
- Test empirico: gli analisti professionali hanno intervalli di confidenza al 90% che contengono il valore reale solo il 40-50% delle volte

**2. Overplacement (Better-than-average effect)**
- Il 93% degli americani ritiene di guidare "meglio della media"
- In finanza: la maggioranza dei gestori attivi ritiene di poter battere il mercato
- Dati reali: solo il 15-20% dei gestori attivi batte l'indice su 10 anni

**3. Overoptimism**
- Sistematica sottovalutazione dei rischi downside
- In IPO: gli analisti buy-side producono stime +30% rispetto ai sell-side

#### Overconfidence e volume di trading
Studi empirici (Odean, Barber) mostrano che:
- Gli uomini tradano il 45% più delle donne
- I trader che tradano di più **guadagnano meno** (costi di transazione + poor timing)
- Il trading eccessivo è uno dei migliori predittori di rendimenti negativi

#### Sistema anti-overconfidence
```
PRIMA DI OGNI TRADE — CHECKLIST OBBLIGATORIA:
□ Ho una tesi contraria credibile? (se non riesci a formularla → bias)
□ Il mio stop loss è definito prima dell'entry? (no = overconfidence sul timing)
□ Sto dimensionando la posizione basandomi su certezza o su R/R?
□ Quante volte ho avuto ragione nell'ultimo mese? (calibration check)
□ Se questo trade va contro di me, avrò ancora la stessa tesi?
```

---

### 3.3 BEHAVIORAL BIASES: CHINA AND RUSSIA EMPIRICAL ANALYSIS
**Fonte:** Alessandra Giancola — LUISS, 2019/2020  
**Supervisore:** Prof. Valentina Peruzzi

#### Bias comportamentali nei mercati ad alta volatilità (rilevante per small cap)

**1. Disposition Effect** (documentato nel mercato cinese)
- Investitori vendono "winners" troppo presto, mantengono "losers" troppo a lungo
- Nel mercato cinese: gli investitori retail chiudono posizioni positive 2.5x più velocemente delle negative
- **Contromisura:** trailing stop su posizioni profittevoli, stop loss meccanico su perdenti

**2. Overconfidence** (amplificato in mercati con forte retail participation)
- Mercato cinese: elevata percentuale di retail (70%+) crea bolle locali
- Pattern: mercati con >60% retail = higher amplitude swings = maggiore asimmetria per chi ha informazioni

**3. Representativeness Heuristic**
- "Questa small cap assomiglia a quella che ha fatto +500% l'anno scorso"
- Problema: seleziona solo i sopravvissuti (survivorship bias nelle analogie)
- **Contromisura:** analisi base rate, non analogia con outliers

**4. Availability Heuristic**
- Sovrastima della probabilità di eventi recenti e vividi
- Post-rally di +200%: "altri rally possibili" sembra più probabile
- **Contromisura:** dati storici base rate invece di esempi recenti vividi

**5. Herding** (cruciale per il sistema speculativo)
- Definizione: copiare il comportamento altrui invece di fare analisi indipendente
- In mercati con bassa liquidità (small cap): il herding crea movimenti amplificati
- **Utilizzo positivo nel sistema:** identificare herding in corso come MOMENTUM SIGNAL
- **Pericolo:** entrare quando il herding è già in fase finale = FOMO = BIRD-type error

#### Market Efficiency nei mercati con strong behavioral component
- **EMH debole** vale raramente nei mercati con alta retail participation
- **Anomalie sfruttabili:** post-earnings drift, momentum, size premium — tutti documentati empiricamente
- **Finestra temporale delle anomalie:** si erodono quando diventano note; necessario aggiornamento continuo del sistema

---

## 4. MODULO RISK — VaR, Monte Carlo, Stress Test

### 4.1 VALUE AT RISK (VaR)
**Fonte:** Aswath Damodaran — capitolo sul VaR  
**Standard industriale:** JP Morgan RiskMetrics

#### Definizione formale
**VaR(α, T):** La perdita massima attesa su un orizzonte T con confidenza α.

*Esempio:* VaR al 95% a 1 settimana di $1,000 = c'è solo il 5% di probabilità che la perdita superi $1,000 in una settimana.

#### 3 metodi di calcolo

**1. Metodo Parametrico (Variance-Covariance)**
```
VaR = μ - z_α × σ × √T

Dove:
- μ = rendimento atteso
- z_α = z-score al livello α (1.645 per 95%, 2.326 per 99%)
- σ = volatilità giornaliera
- T = orizzonte temporale
```
*Assunzione critica:* rendimenti normalmente distribuiti (FALSO in pratica → fat tails!)

**2. Simulazione Storica**
- Applica i rendimenti storici al portafoglio corrente
- Ordina per perdita → il VaR è il 5° percentile
- Pro: non assume distribuzione normale
- Con: il passato non predice il futuro (regime changes!)

**3. Monte Carlo**
- Simula migliaia di scenari di prezzo
- Il VaR è il percentile desiderato della distribuzione simulata
- Più accurato ma computazionalmente costoso

#### Limiti critici del VaR (essenziali per il sistema)

| Limitazione | Descrizione | Impatto pratico |
|------------|-------------|-----------------|
| **Non sub-additivo** | VaR(A+B) può essere > VaR(A) + VaR(B) — illusione di diversificazione | Non sommare VaR di posizioni diverse |
| **Ignora tail risk** | VaR al 95% dice niente sulla forma della coda nel 5% peggiore | Usare CVaR / Expected Shortfall |
| **Distribuzione normale** | Rendimenti finanziari hanno fat tails | Le perdite reali >VaR sono molto più frequenti del previsto |
| **Regime blindness** | Calcolato su dati storici che non includono il regime corrente | Aggiornare parametri in tempo reale |

#### CVaR (Conditional VaR / Expected Shortfall) — misura superiore
```
CVaR = E[Loss | Loss > VaR]
```
Misura la **perdita attesa NEL caso peggiore**, non solo la soglia. Più appropriato per sistemi speculativi.

#### Applicazione pratica al sistema
```
Per ogni posizione aperta:
- Calcola VaR giornaliero al 95%
- Definisce stop loss = max(VaR × 2, structural invalidation level)
- Sizing: rischio massimo per trade = 1-2% del capitale totale
- Portfolio VaR: somma VaR singoli × correlation factor (non assumere indipendenza!)
```

---

### 4.2 MONTE CARLO METHODS IN FINANCIAL ENGINEERING
**Fonte:** Paul Glasserman — Columbia/Princeton (libro da Columbia lecture notes)  
**Applicazione core:** Simulazione scenari, pricing derivati, validazione probabilistica

#### Principio fondamentale
Il Monte Carlo in finanza si basa sul **risk-neutral pricing**: sotto la misura Q (rischio-neutrale), i prezzi degli asset crescono al risk-free rate, e il valore atteso di qualsiasi payoff è il suo prezzo corretto.

**Processo di base (GBM — Geometric Brownian Motion):**
```
dS = μS dt + σS dW

Discretizzato:
S(t+Δt) = S(t) × exp[(μ - σ²/2)Δt + σ√Δt × Z]

Dove Z ~ N(0,1)
```

#### Implementazione pratica nel sistema speculativo

**Obiettivo:** Non prezzare derivati, ma **validare scenari di prezzo** per una posizione swing.

```python
# Pseudocodice simulazione Monte Carlo per trade swing
import numpy as np

def simulate_trade(S0, mu, sigma, T, n_sim=10000):
    """
    S0: prezzo entry
    mu: drift atteso (annualizzato)
    sigma: volatilità storica (annualizzata)
    T: orizzonte in anni (es. 10 giorni = 10/252)
    """
    daily_returns = np.random.normal(
        (mu - 0.5 * sigma**2) / 252,
        sigma / np.sqrt(252),
        (n_sim, int(T * 252))
    )
    price_paths = S0 * np.exp(np.cumsum(daily_returns, axis=1))
    final_prices = price_paths[:, -1]
    return final_prices

# Output operativo
S0 = 5.50  # entry price
target = 7.80  # T1
stop = 4.20  # stop loss

results = simulate_trade(S0=S0, mu=0.30, sigma=0.85, T=14/252)
prob_target = np.mean(results >= target)
prob_stop = np.mean(results <= stop)
prob_neutral = 1 - prob_target - prob_stop

print(f"Prob raggiungere target: {prob_target:.1%}")
print(f"Prob stop loss: {prob_stop:.1%}")
print(f"EV del trade: {prob_target*(target-S0) + prob_stop*(stop-S0):.2f}")
```

#### Variance Reduction Techniques (per simulazioni più accurate)

**Antithetic Variates:** Per ogni Z generato, usare anche -Z → dimezza la varianza dell'estimatore senza costo computazionale.

**Control Variates:** Usi una variabile correlata con payoff noto per ridurre varianza.

**Importanza Sampling:** Concentra la simulazione nella coda della distribuzione → utile per tail risk.

#### Applicazione al sistema: GBM formula nella speculative-continuation-engine
La Fase di validazione probabilistica del sistema usa esattamente questo framework per calcolare:
- Probabilità di raggiungere T1, T2, T3
- Expected Value del trade
- Percentile di stop loss hit

---

### 4.3 STRESS TEST SCENARIOS
**Fonte:** Ryu — Stress Test Scenarios (documento pratico, 9 pagine)

#### Framework di Stress Testing
Lo stress test risponde a: **"Cosa succede al mio portafoglio in scenari estremi MA storicamente plausibili?"**

Diverso dal VaR perché:
- Non cerca un percentile statistico
- Definisce scenari narrativi specifici e quantifica l'impatto

#### Scenari standard da integrare nel sistema

**Scenario 1 — Fed Shock (2022-style)**
- Fed hiking aggressivo: +400bps in 12 mesi
- Impatto: Growth stocks -40%, Value -20%, Cash/T-bills +4%
- Small cap high-beta: -50 to -70%

**Scenario 2 — Flash Crash (2010, 2020-style)**
- Calo intraday -10% su SPY in 30 minuti
- Volatilità implicita (VIX) da 15 a 80 in ore
- Bid-ask spread small cap: 5-10x normale
- **Implicazione:** stop loss market order può slippage del 15-20% oltre il livello!

**Scenario 3 — Geopolitical Shock**
- Escalation militare improvvisa (Russia-NATO, Taiwan)
- Safe haven: oro, USD, CHF
- Risk-off: emerging markets, energy dipendenti

**Scenario 4 — Sector-Specific Collapse**
- FDA rejects multiple drugs → biotech -40% settoriale
- Export restrictions → semiconductor -30%
- **Implicazione:** anche setup con catalyst eccellenti possono collassare per contagio settoriale

#### Applicazione pratica: Pre-Trade Stress Test Check
```
Prima di ogni entry >1% sizing:
□ Se VIX sale da X a X+20, questo trade tiene?
□ Se il settore cala -20% (contagio), dove finisce la posizione?
□ Se viene annunciato un evento macro avverso entro 48h, esco?
□ Ho liquidità sufficiente per sopportare un margin call temporaneo?
□ Il mio stop loss regge a slippage del 5%?
```

---

## 5. MODULO PORTFOLIO — Costruzione, Allocazione, Fattori

### 5.1 VANGUARD'S PORTFOLIO CONSTRUCTION FRAMEWORK
**Fonte:** Roger Aliaga-Díaz et al. — Vanguard Investment Strategy Group  
**Target:** Institutional portfolio construction — adattato per sistema speculativo

#### I 4 pilastri del portfolio construction framework

**PILASTRO 1 — Goals-Based Framework**
Ogni portafoglio deve essere costruito attorno a obiettivi specifici, non a benchmark:
- Obiettivo del sistema speculativo: **asimmetria +R/R**, non tracking error vs indice
- Metrica di successo: **R multiplo realizzato** (rendimento / rischio preso), non solo % guadagno

**PILASTRO 2 — Asset Allocation come driver primario**
- Studi empirici: il 90%+ della variabilità dei rendimenti è spiegato dall'asset allocation
- La selezione dei singoli titoli contribuisce solo marginalmente al lungo termine
- **Implicazione per il sistema:** il timing del regime conta più della selezione del singolo titolo

**PILASTRO 3 — Costo e Fiscalità**
- Ogni % di commissioni riduce il rendimento composto in modo amplificato nel tempo
- **Formula impatto commissioni:**
  ```
  Dopo N anni: (1 + r_netto)^N vs (1 + r_lordo)^N
  Differenza su 10 anni con 2% commissioni annue: ~18% capitale perso
  ```
- Per il sistema speculativo (IBKR): massimizzare operazioni ad alto R/R per ammortizzare i costi

**PILASTRO 4 — Diversification without Diworsification**
- Diversificazione riduce il rischio non sistematico (idiosincratico)
- Oltre un certo numero di posizioni, il rischio non scende ulteriormente
- Per portafogli speculativi: 3-5 posizioni è l'optimum (alta concentrazione + gestione attiva)
- Regola del sistema: **UN solo bullet** per il setup Layer 1 (massima concentrazione)

#### Vanguard's Efficient Frontier per portafogli speculativi
```
Max Sharpe Ratio per portafoglio concentrato:
- Asset con correlazione bassa o negativa
- Asset con catalyst indipendenti (no settore unico)
- Asset con timing di catalyst diversificato (non tutte le posizioni in scadenza lo stesso giorno)
```

---

### 5.2 ASSET ALLOCATION AND RISK MANAGEMENT
**Fonte:** Capitolo dedicato — framework integrato

#### Mean-Variance Optimization (Markowitz, 1952)

**La frontiera efficiente:**
```
Min σ²_p = Σ_i Σ_j w_i w_j σ_ij

Subject to: Σ w_i = 1, E[R_p] = target
```

**Problemi pratici del MVO:**
- Estremamente sensibile agli input (piccoli errori in μ → grandi errori nell'allocazione)
- Produce soluzioni corner (tutto in 1-2 asset)
- Ignora il tail risk
- Le correlazioni cambiano in regime di stress (aumentano drammaticamente in crash)

**Black-Litterman model (soluzione al MVO):**
Combina le view del gestore con gli equilibri di mercato impliciti, producendo allocazioni più stabili.

#### Correlazioni in regime di stress
**Il problema più critico per il sistema speculativo:**

Le correlazioni tra asset tendono a **1** durante i crash di mercato:
- In condizioni normali: SPY vs BTC correlazione 0.15
- Durante crash (marzo 2020): correlazione salì a 0.85

**Implicazione:** La diversificazione fallisce esattamente quando ne hai più bisogno.

**Soluzione nel sistema:**
- Mantenere sempre una quota in cash durante regime HIGH VOLATILITY
- Non considerare diversificazione settoriale come protezione in scenario di panic selling
- Stop loss definiti PRIMA, non dopo che le correlazioni sono già salite

#### Rebalancing ottimale
- Studi empirici: rebalancing sistematico (threshold-based > calendar-based) produce rendimenti migliori
- Rebalancing prematuro = perdere momentum
- Rebalancing troppo tardivo = permettere concentrazione eccessiva

---

### 5.3 FAMA-FRENCH THREE FACTOR MODEL
**Fonte:** Eugene F. Fama & Kenneth R. French — *Journal of Financial Economics*, 1993

#### Il modello
```
E[R_i] - R_f = β_i(E[R_M] - R_f) + s_i × SMB + h_i × HML

Dove:
- R_f = risk-free rate
- E[R_M] - R_f = market premium (≈ 6-8% annuo storicamente)
- SMB = Small Minus Big (small cap premium ≈ 2-3% annuo)
- HML = High Minus Low B/M (value premium ≈ 3-4% annuo)
```

#### Implicazioni empiriche chiave

**Small cap premium (SMB):**
- Le small cap storicamente battono le large cap di ~3% annuo **risk-adjusted**
- Ma: alta volatilità, illiquidità, maggiori drawdown
- **Cruciale per il sistema:** l'universo di small/micro-cap è il terreno naturale di hunting per il sistema speculativo

**Momentum factor (Carhart, 1997 — estensione Fama-French):**
```
WML = Winners Minus Losers (12 mesi precedenti, escluso ultimo mese)
Premium: ≈ 7-10% annuo
```
- I titoli che hanno performato meglio nei 12 mesi precedenti tendono a continuare nel breve periodo
- **Applicazione nel sistema:** volume ratio + price momentum = segnale di setup

**Perché il sistema funziona sui fattori:**
- Small cap + high momentum + positive catalyst = **triple factor loading**
- La convergenza di 3 fattori documentati aumenta la probabilità di edge reale

---

### 5.4 MIT 15.401 FINANCE THEORY I — LECTURE 8: PORTFOLIO THEORY
**Fonte:** Alex Stomper — MIT Sloan School of Management  
**Riferimenti:** Brealey/Myers/Allen, Bodie/Kane/Marcus

#### Portfolio Returns
Per un portafoglio di N asset:
```
E[R_p] = Σ w_i E[R_i]

σ²_p = Σ_i Σ_j w_i w_j Cov(R_i, R_j)
     = Σ_i w²_i σ²_i + 2 Σ_i<j w_i w_j ρ_ij σ_i σ_j
```

#### Diversificazione: quanto basta?
- Con 20-30 asset NON correlati, il rischio non sistematico è quasi completamente eliminato
- Il rischio residuo è solo il rischio sistematico (beta di mercato)
- **Per il sistema speculativo (3-5 asset):** il rischio non sistematico è intenzionalmente alto = source of alpha

#### Sharpe Ratio
```
Sharpe = (E[R_p] - R_f) / σ_p
```
- Misura il rendimento per unità di rischio totale
- Un Sharpe >1 è eccellente; >2 è straordinario
- **Per sistemi speculativi:** più significativo il Calmar Ratio (return/max drawdown)

#### Systematic vs Non-Systematic Risk
```
Total Risk = Systematic Risk (β × market) + Idiosyncratic Risk (ε)

Systematic risk: non eliminabile con diversificazione
Idiosyncratic: eliminabile → ma è la source of alpha nel sistema!
```

---

### 5.5 PORTFOLIO THEORY (TESTO ACCADEMICO)
**Fonte:** Testo di Portfolio Theory — capitoli su ottimizzazione e selezione asset

#### Capital Asset Pricing Model (CAPM)
```
E[R_i] = R_f + β_i (E[R_M] - R_f)

β_i = Cov(R_i, R_M) / Var(R_M)
```

**Limiti del CAPM:**
- Assume mercati perfetti (no transaction costs, no taxes)
- Assume distribuzione normale dei rendimenti
- Assume che tutti gli investitori abbiano le stesse aspettative
- Empiricamente: il beta da solo spiega solo il 30% delle variazioni cross-sectional

**Applicazione pratica:**
- Un titolo con β > 1 si muove più del mercato (high-beta = high-upside MA high-downside)
- Per il sistema speculativo: selezionare asset ad alto beta in regime bull, basso beta in regime incerto

#### Security Market Line (SML)
```
Plot: E[R] vs β
- Asset sopra la SML: underpriced (alpha positivo) → BUY
- Asset sotto la SML: overpriced (alpha negativo) → SELL/AVOID
```

---

## 6. MODULO HEDGE FUND — Strategie, Alpha, Replica

### 6.1 A PRIMER ON HEDGE FUNDS
**Fonte:** Paper introduttivo — struttura e strategie hedge fund

#### Definizione e struttura
Un hedge fund è un veicolo di investimento privato che:
- Usa leva finanziaria
- Va sia long che short
- Ha struttura fee "2&20" (2% management + 20% performance)
- Accesso limitato a investitori qualificati

#### Principali strategie hedge fund

| Strategia | Descrizione | Applicazione al sistema |
|-----------|-------------|------------------------|
| **Long/Short Equity** | Long su undervalued, short su overvalued | Sistema: solo long, no short |
| **Global Macro** | Scommesse su macro (tassi, valute, commodity) | Regime detector + macro driver |
| **Event-Driven** | M&A, ristrutturazioni, catalyst | Core del sistema speculativo |
| **Statistical Arbitrage** | Mean reversion quantitativa | Parzialmente in continuation engine |
| **Distressed** | Securities in default o near-default | Non nel sistema |
| **CTA / Trend Following** | Momentum su future | Momentum filter nel sistema |

#### Fee structure e incentivi
- 2&20: l'hedge fund guadagna anche in anni negativi (2% management fee)
- High watermark: il 20% si paga solo su nuovi massimi
- **Implicazione:** i gestori HF hanno incentivo ad assumere rischio nel Q4 se sono indietro

---

### 6.2 HEDGE FUND REPLICATION: THE GLOBAL MACRO CASE
**Fonte:** Paper accademico — replicazione strategie Global Macro  
**56 pagine**

#### Global Macro: la strategia più difficile da replicare
I fondi Global Macro (Soros, Druckenmiller) basano i trade su:
1. Analisi macroeconomica approfondita dei paesi/regioni
2. Identificazione di squilibri insostenibili
3. Posizionamento prima della correzione
4. Leva alta su trade ad alta conviction

**Esempio storico:** Soros vs Sterlina britannica (1992)
- Identificò che il tasso di cambio fisso era insostenibile (alti tassi UK necessari per ERM vs economia debole)
- Accumulò short sulla sterlina per settimane
- Guadagnò ~$1 miliardo in un giorno quando la sterlina uscì dall'ERM

#### Replication Factor Model
Il rendimento di un Global Macro fund si può approssimare con:
```
R_HF ≈ α + β_1(Equity Premium) + β_2(FX Carry) + β_3(Commodity Trend) 
       + β_4(Bond Momentum) + ε
```

**Per il sistema speculativo:**
L'approccio Global Macro si traduce nel regime detector: prima di qualsiasi trade, inquadrare il contesto macro (Fed, dollaro, tassi, commodity) per capire la direzione della marea. Non nuotare contro di essa.

---

### 6.3 HEDGE FUND PORTFOLIO CONSTRUCTION
**Fonte:** Libro completo — 93 pagine — costruzione portafoglio HF

#### Principi di costruzione portafoglio istituzionale

**1. Risk Budgeting vs Capital Budgeting**
- Il capitale non è allocato in proporzione, ma il **rischio** sì
- Se una posizione ha volatilità doppia, le si dà metà del capitale per avere uguale risk contribution

```
Risk parity allocation:
w_i = (1/σ_i) / Σ(1/σ_j)

Invece di:
w_i = target allocation / n_positions
```

**2. Portfolio-Level Drawdown Control**
- HF istituzionali definiscono un **portfolio stop loss** (es. -15% da peak)
- Se raggiunto, TUTTO viene liquidato e si ricostruisce con minore leva
- **Per il sistema:** definire un portfolio stop loss mensile (es. -20% del capitale speculativo)

**3. Gross vs Net Exposure**
```
Gross exposure = |Long| + |Short| (leva totale)
Net exposure = Long - Short (direzione del mercato)

Sistema (solo long):
Gross = Net = somma posizioni long
```

**4. Factor Exposure Management**
- I migliori HF gestiscono l'**exposure ai fattori**, non solo ai singoli titoli
- Evitare concentration su stesso fattore (es. tutte le posizioni high-momentum small cap in AI)

#### Liquidità e costruzione del portafoglio
- Gli asset illiquidi (small cap con float <1M) devono avere position size ridotta per via del **market impact**
- Regola pratica: **posizione ≤ 1-2% dell'ADV (Average Daily Volume)**
- Con ADV 500K e position size 2K: market impact trascurabile ✓

---

### 6.4 HEDGE FUND DUE DILIGENCE AS A SOURCE OF ALPHA
**Fonte:** Paper — framework di selezione e valutazione

#### Due Diligence Framework — adattato per il sistema

Il framework istituzionale di DD si traduce nel sistema speculativo nel processo di **catalyst verification**:

**LIVELLO 1 — Verifica del catalyst**
- Fonte primaria: 8-K SEC filing
- Il catalyst è reale o è marketing?
- C'è un contratto firmato o solo un MOU (Memorandum of Understanding)?
- Il financing è confermato (term sheet firmato) o solo "in discussione"?

**LIVELLO 2 — Track record del management**
- Il CEO ha già realizzato quanto promette?
- C'è insider buying recente?
- La storia di guidance precedente è stata rispettata?

**LIVELLO 3 — Red flags strutturali**
- Il float è artificialmente basso (warrant + convertibili)?
- Ci sono lock-up expiry imminenti?
- Il reverse split recente ha distrutto value?
- C'è relazione pagata tra CEO e newsletter/promotori?

---

### 6.5 HEDGE FUND PERFORMANCE, RISK AND CAPITAL FORMATION
**Fonte:** Paper accademico empirico — analisi performance HF

#### Findings empirici chiave

**Persistenza della performance:**
- Gli HF top quartile hanno ~40% probabilità di rimanere top quartile l'anno successivo
- Vs il 25% atteso per caso → esiste alpha persistente MA è raro
- La maggior parte degli "alpha" sono in realtà **factor premiums** (momentum, small cap, value)

**Survivorship bias:**
- I database HF escludono i fondi chiusi
- Il rendimento medio apparente degli HF è ~3-4% più alto del rendimento reale (survivorship bias)
- **Applicazione al sistema:** non valutare la strategia solo sui trade vincenti

**Crisis Alpha:**
- Alcuni HF (soprattutto CTA/trend-following) guadagnano durante i crash
- Spiegazione: i momentum systems vanno short quando i trend si invertono
- **Il sistema speculativo NON ha questa caratteristica** → necessario uscire PRIMA dei crash

---

### 6.6 EXTRACTING PORTABLE ALPHA FROM LONG/SHORT HEDGE FUNDS
**Fonte:** Paper accademico — separazione alpha da beta

#### Portable Alpha: il concetto
```
Return = Alpha (skill) + Beta × Market Return

Se separi il beta (mediante short futures o ETF):
→ Rimane solo l'alpha "portabile" → deployabile su qualsiasi beta base
```

**Applicazione pratica al sistema:**
L'edge del sistema speculativo deve essere:
- **Timing edge:** entri prima che il catalyst sia priced in
- **Information edge:** hai verificato il catalyst prima degli altri
- **Execution edge:** entri nel range ottimale (pull-back, non breakout chase)

**Ciò che NON è alpha nel sistema:**
- Guadagnare perché l'intero mercato è salito (beta exposure)
- Guadagnare perché il settore era hot (sector beta)
- Il vero alpha è guadagnare su setup specifici IN QUALSIASI REGIME

---

## 7. MODULO QUANTITATIVE — Sistemi, Backtesting, Execution

### 7.1 QUANTITATIVE TRADING — ERNIE CHAN (2009)
**Fonte:** Ernest P. Chan — *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*, Wiley 2009

#### Principi fondamentali del trading sistematico

**Cap. 2 — Come identificare una strategia**
Criteri di valutazione di uno strategy idea:
1. **Sharpe Ratio** > 1 (idealmente > 2) sul backtesting
2. **Max Drawdown** < 20% (se maggiore, position size deve essere ridotta proporzionalmente)
3. **Transaction costs:** calcolare sempre il round-trip cost PRIMA di valutare profitabilità
4. **Survivorship bias free:** i dati storici devono includere titoli poi delistati
5. **Data-snooping bias:** più parametri hai ottimizzato, meno il backtesting è affidabile

**La trappola del data snooping:**
```
Se esplori N strategie sullo stesso dataset e ne selezioni 1:
La probabilità che quella 1 sembri buona per caso = molto alta!

Regola pratica Chan:
- Testa la strategia out-of-sample su dati MAI visti prima
- Usa un "hold-out set" di almeno 30% dei dati
- Il Sharpe out-of-sample deve essere ≥ 50% del in-sample
```

#### Cap. 6 — Money and Risk Management

**Kelly Formula (Optimal f):**
```
f* = (μ - r) / σ²

Dove:
- μ = rendimento atteso della strategia
- r = risk-free rate
- σ² = varianza dei rendimenti

f* = frazione ottimale del capitale da rischiare
```

**In pratica: Half-Kelly o Quarter-Kelly**
Il Kelly intero massimizza il rendimento a lungo termine ma produce drawdown estremi.
- **Half-Kelly:** riduce il drawdown del 50% con solo 25% di riduzione del rendimento
- **Quarter-Kelly:** più conservativo, raccomandata per sistemi non perfettamente calibrati

**Esempio per il sistema ($2,000 capitale single bullet):**
```
Assumendo:
- Win rate stimato: 55%
- Average win: +40%
- Average loss: -25%

Kelly fraction: f* = (0.55 × 0.40 - 0.45 × 0.25) / (0.40 × 0.25)
                   ≈ (0.22 - 0.1125) / 0.10 ≈ 1.075

Full Kelly = 107% del capitale → irrazionale
Half Kelly = 53% → ancora alto
Quarter Kelly = 27% → sizing ragionevole per rischio
```

#### Cap. 7 — Mean-Reverting vs Momentum Strategies

**Mean Reversion:**
- Funziona in mercati laterali, range-bound
- Indicatori: RSI estremi, Bollinger Bands
- Rischio: trend continuation può produrre perdite illimitate se non c'è stop

**Momentum:**
- Funziona in mercati con forte trend direzionale
- Documentato empiricamente: 12-month momentum persiste per 3-12 mesi
- Il sistema speculativo è MOMENTUM-BASED (entra nel trend, non contro di esso)

**Regime Switching tra i due:**
```
Regime test: ADF (Augmented Dickey-Fuller)
- p-value < 0.05: stazionario → mean reversion
- p-value > 0.05: non-stazionario → momentum/trend
```

#### Cap. 7 — Cointegration per pairs trading
```
Se P_1 e P_2 sono cointegrate:
Z = P_1 - β × P_2 è stazionario (mean-reverting)

Trade: quando Z devia di >2σ dalla media:
→ Short il più caro, Long il più economico
→ Target: Z torna alla media
```

---

### 7.2 GAME THEORY APPLICATIONS (Kolokol'tsov & Malafeyev)
**Fonte:** *Understanding Game Theory* — Warwick/St. Petersburg

#### Equilibri e comportamento strategico nei mercati

**Nash Equilibrium nei mercati:**
In un mercato con N partecipanti, nessuno ha incentivo a deviare unilateralmente dalla strategia di equilibrio. **Ma:** gli equilibri di mercato sono multipli e fragili nelle condizioni di stress.

**Prisoner's Dilemma applicato al trading:**
- Tutti i trader hanno incentivo a vendere al primo segnale di panico
- Ma se tutti vendono → crollo → perdono tutti
- Il "best response" individuale porta al "worst outcome" collettivo
- **Implicazione:** nei crash, il panico si auto-alimenta razionalmente

**Signaling e informazione asimmetrica:**
- Gli insider sanno più del mercato
- I loro trades sono segnali (imperfetti) di informazione privata
- Insider buying recente = segnale di alta conviction del management

**Game Theory e market microstructure:**
- Market makers fissano bid-ask spread basandosi sulla probabilità di tradare con informed traders
- Spread più ampi in titoli con alta probabilità di insider knowledge
- **Implicazione:** spread ampi su small cap = normale, non necessariamente red flag

---

## 8. FRAMEWORK OPERATIVO INTEGRATO

### 8.1 PIPELINE DECISIONALE COMPLETA

```
═══════════════════════════════════════════════════════════════
FASE -1 | SERALE (22:00-23:00 IT) — OBBLIGATORIA OGNI GIORNO
═══════════════════════════════════════════════════════════════

1. SCAN EARNINGS AH (qualsiasi settore, $1-25)
   → EPS beat >25% o Revenue beat >20%
   → Prezzo range $1-7 (layer 1 bullet) o $1-25 (layer 2 swing)

2. SCAN 8-K SEC FILINGS (dopo 16:00 ET)
   → Contratti, acquisizioni, financing, catalyst TIER 1

3. AH MOVERS (stockmarketwatch.com/movers/afterhours)
   → Volume ratio >10x
   → Float <15M

4. CATALYST CLASSIFICATION
   → TIER 1: 8-K verificato + financing reale → actionable
   → TIER 2: speculativo con base credibile → sizing ridotto
   → TIER 3: MOU non vincolante, AI-washing, reverse split → SKIP

5. OUTPUT: WATCHLIST SERALE (max 3 titoli)
   → Con tesi preliminare, entry range, stop ipotetico

═══════════════════════════════════════════════════════════════
FASE 0 | PREMARKET (10:00-14:00 IT) — SCANNER MATTINA
═══════════════════════════════════════════════════════════════

1. MARKET REGIME CHECK
   □ VIX trend: □ SPY direction: □ DXY: □ 10Y yield:
   → TRADE / SELECTIVE / NO TRADE

2. VERIFICA WATCHLIST SERALE
   → Il catalyst è ancora valido?
   → Ci sono nuove notizie che cambiano la tesi?
   → Il premarket volume conferma l'interesse?

3. PREMARKET MOVERS
   → stockanalysis.com/markets/premarket/gainers
   → Volume ratio premarket vs ADV

4. TECHNICAL SETUP (se regime = TRADE/SELECTIVE)
   → Struttura H4/D1: BOS confermato?
   → FVG identificato: zona di interesse per entry?
   → Stop level: sotto ultimo CHoCH o swing low strutturale

═══════════════════════════════════════════════════════════════
FASE 1 | SILENZIO APERTURA (15:30-15:35 IT)
═══════════════════════════════════════════════════════════════

NESSUNA AZIONE — solo osservazione
Il mercato "scopre" il prezzo di apertura nei primi 5 minuti
Volatilità artificiale, spread amplificati, falsi segnali

═══════════════════════════════════════════════════════════════
FASE 2 | FINESTRA ENTRY (15:35-15:45 IT)
═══════════════════════════════════════════════════════════════

CONDIZIONI PER ENTRY:
□ Pull-back confermato dal picco di apertura (almeno -3%)
□ Volume in calo durante il pull-back (non distribuzione)
□ Prezzo in zona FVG o supporto identificato
□ Catalyst ancora intatto (nessuna nuova notizia avversa)
□ Stop loss definito e accettato prima del click

SIZING:
- Layer 1 bullet: $2,000 — UN solo trade
- Stop max: -25% (~$500 rischio reale)
- Non entrare se il rischio supera questo threshold

═══════════════════════════════════════════════════════════════
FASE 3 | GESTIONE POSIZIONE (15:45 → chiusura)
═══════════════════════════════════════════════════════════════

TRAILING STOP (SMC-based):
- Sposta stop SOLO dopo nuovo BOS confermato verso l'alto
- Mai scendere sotto il floor di gain (+8/9%)
- Se raggiunge T1: rimuovi rischio (close 33-50%), trailing sul resto

REGOLA DELLE 3 CANDELE:
- Se prezzo non si muove nella direzione attesa in 3 candele 15min → revisione tesi
- Non è obbligo uscire, ma rivalutare

INVALIDATION:
- Se il catalys viene contraddetto da nuove notizie → exit immediata
- Se il prezzo chiude sotto lo stop strutturale → exit end of day
```

---

### 8.2 FRAMEWORK CATALYST TIER SYSTEM

```
╔══════════════════════════════════════════════════════════════╗
║  CATALYST CLASSIFICATION — TIER SYSTEM                       ║
╠══════════════════════════════════════════════════════════════╣
║  TIER 1 — ACTIONABLE (alto sizing permesso)                  ║
║  ✓ 8-K SEC depositato con contratto firmato                  ║
║  ✓ FDA approval / PDUFA positive outcome                     ║
║  ✓ Earnings beat con guidance raise su revenue               ║
║  ✓ Financing istituzionale reale (term sheet firmato)        ║
║  ✓ Contratto DoD/governo con valore >30% market cap          ║
║  ✓ M&A announcement con prezzo e termine definiti           ║
╠══════════════════════════════════════════════════════════════╣
║  TIER 2 — SPECULATIVO (sizing ridotto, stop più stretto)    ║
║  ⚠ MOU con controparte nota ma non vincolante               ║
║  ⚠ Partnership annunciata senza termini finanziari           ║
║  ⚠ Trial clinico in corso (non ancora PDUFA)                ║
║  ⚠ Contratto "pending regulatory approval"                   ║
║  ⚠ Guidance raise senza catalysts concreti                  ║
╠══════════════════════════════════════════════════════════════╣
║  TIER 3 — SKIP (nessun trade)                               ║
║  ✗ MOU non vincolante con entità sconosciute                ║
║  ✗ AI-washing (cambio nome/pivot senza prodotto reale)      ║
║  ✗ Reverse split recente (<6 mesi)                          ║
║  ✗ Titolo già +300% senza pull-back                         ║
║  ✗ Promozione pagata / newsletter pump                      ║
║  ✗ Blow-off day 3+ (parabola verticale senza catalysts)     ║
╚══════════════════════════════════════════════════════════════╝
```

---

### 8.3 PATTERN LIBRARY — 6 PATTERN AD ALTA PROBABILITÀ

#### PATTERN #1 — Shell-Pivot-AI (BIRD-type)
```
Setup: shell azienda + cessione business legacy + pivot AI/tech + financing reale
Catalyst: 8-K depositato la sera precedente
Timing: entry la mattina del giorno 1 (non dopo +300%)
Expected move: +50% a +876% giorno 1
Stop: -20-25% dal picco intraday dopo entry
```

#### PATTERN #2 — FDA PDUFA Pre-Run
```
Setup: biotech micro-cap con PDUFA entro 14 giorni
Entry: 2 settimane prima della data (pre-run window)
Catalyst: approvazione FDA con probabilità >50%
Expected move: +50-200% pre-PDUFA, eventuale +300% on approval
Stop: strutturale sotto ultimo swing low significativo
Exit: 50% prima del PDUFA day (riduzione del binary risk)
```

#### PATTERN #3 — Short Squeeze da Catalyst
```
Setup: Short Interest >30% float + notizia inattesa positiva
Catalyst: earnings beat / partnership / FDA
Expected move: amplificato dal forced covering degli short
Identificazione: verificare SI su finviz/shortsqueeze.com prima dell'entry
Stop: se price action debole entro prime 2 ore = uscita (squeeze non scattato)
```

#### PATTERN #4 — Defense Contract Micro-Cap
```
Setup: contratto DoD/NATO >30% della market cap annunciato
Catalyst: comunicato stampa + SEC filing che confirma importo
Expected move: +30-150% entro 1-3 settimane
Settori: difesa, drone, cybersecurity, sensoristica
Stop: -20% dall'entry
```

#### PATTERN #5 — Pre-Earnings Run
```
Setup: earnings in 5-15 giorni + consensus pessimista + struttura tecnica bullish
Catalyst: sottostima degli analisti documentata (es. guidance precedente alzata)
Expected move: +15-40% nel periodo pre-earnings
Exit rule: CHIUDERE prima degli earnings (non tenere il binary risk)
Stop: -15% dall'entry
```

#### PATTERN #6 — Continuation Setup (5-7 giorni)
```
Setup: titolo che ha già fatto +25-50% in 5 giorni con pull-back ordinato
Catalyst: originale ancora intatto, nessuna nuova notizia avversa
Volume: calo del volume nel pull-back (accumulo, non distribuzione)
Technical: pull-back fermato su FVG o EMA 21
Expected move: +15-30% nel follow-through
Stop: sotto il minimo del pull-back
```

---

### 8.4 ANTI-PATTERN LIBRARY — 9 ERRORI DOCUMENTATI

| Anti-Pattern | Descrizione | Regola correttiva |
|--------------|-------------|-------------------|
| **#1 FOMO Chase** | Entrare dopo +200% perché "può salire ancora" | BIRD-rule: dopo +300% = NO TRADE assoluto |
| **#2 Filtro Settoriale a Priori** | "Non seguo l'ad-tech" → miss sistematici | La Fase -1 scansiona TUTTI i settori |
| **#3 Hold Loser / Close Winner** | Tener perdenti "aspettando il recupero" | Stop loss meccanico, trailing su vincenti |
| **#4 Post-Mortem Mancato** | Trade sbagliato non analizzato → errore ripetuto | Post-mortem scritto entro 24h da ogni loss |
| **#5 Over-diversificazione** | 15 posizioni small = nessun impatto | Max 3-5 posizioni, una sola bullet Layer 1 |
| **#6 Silenzio Apertura Violato** | Entry nei primi 5 minuti di mercato | Finestra entry solo 15:35-15:45 IT |
| **#7 Stop Loss Post-Entry** | Definire lo stop dopo l'entry | Stop PRIMA dell'entry, sempre |
| **#8 Catalyst Non Verificato** | Tradare su titolo "sentito parlare" | Verifica 8-K/comunicato stampa obbligatoria |
| **#9 Attesa Eccessiva** | "Aspetto conferma a 5 giorni" = miss | Con $2K e -25% stop, non serve conferma lunga |

---

## 9. REGOLE NON NEGOZIABILI

```
╔══════════════════════════════════════════════════════════════╗
║  10 COMMANDMENTS DEL SISTEMA SPECULATIVO                     ║
╠══════════════════════════════════════════════════════════════╣
║  1. NO TRADE senza catalyst TIER 1/2 verificato             ║
║     Cash è una posizione valida. Aspetta il setup.          ║
║                                                              ║
║  2. Stop loss PRIMA dell'entry, mai dopo                    ║
║     Se non sai dove stai sbagliando, non entrare.           ║
║                                                              ║
║  3. Titolo già +300% in 1 giorno = NO TRADE assoluto        ║
║     Il denaro si fa PRIMA del blow-off, non dopo.           ║
║                                                              ║
║  4. MOU non vincolante = TIER 3 = SKIP                      ║
║     Parole non valgono nulla. Solo contratti firmati.       ║
║                                                              ║
║  5. Nessun filtro settoriale nello scouting                 ║
║     I dati vengono prima. I settori vengono dopo.           ║
║                                                              ║
║  6. Trailing stop SMC: si sposta SOLO dopo BOS confermato  ║
║     Mai sotto il floor di gain (8-9%)                       ║
║                                                              ║
║  7. Silenzio apertura NYSE: 15:30-15:35 IT                 ║
║     Finestra entry: 15:35-15:45 IT su pull-back confermato ║
║                                                              ║
║  8. Fase -1 serale è OBBLIGATORIA ogni giorno               ║
║     Il sistema si alimenta di informazioni fresche.         ║
║                                                              ║
║  9. Layer 1 e Layer 2: capitali separati, non comunicanti  ║
║     Un loss intraday non finanzia una swing e viceversa.    ║
║                                                              ║
║  10. Post-mortem entro 24h su ogni loss significativo       ║
║      L'errore non analizzato è un errore futuro garantito.  ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 10. FONTI E CREDENZIALI

### Documenti Primari nel Progetto

| # | Titolo | Autore/Fonte | Anno | Dominio | Priorità |
|---|--------|-------------|------|---------|----------|
| 1 | Macroeconomic Regimes and Regime Shifts | James D. Hamilton — NBER | 2016 | Macro | ⚡ ALTA |
| 2 | This Time Is Different | Reinhart & Rogoff — NBER | 2008 | Macro/Storico | ⚡ ALTA |
| 3 | Manias, Panics, and Crashes | Charles P. Kindleberger | 5th ed. | Macro/Behavioral | ⚡ ALTA |
| 4 | Global Transmission of US Monetary Policies | Paper accademico | var. | Macro | ⚡ ALTA |
| 5 | Behavioral Model of the Dot-Com Bubble | Paper accademico | var. | Behavioral/Macro | MEDIA |
| 6 | Prospect Theory | Kahneman & Tversky — JE | 1979 | Behavioral | ⚡ ALTA |
| 7 | Overconfidence in Financial Markets | Paper accademico | var. | Behavioral | ⚡ ALTA |
| 8 | Behavioral Biases: China and Russia | Giancola — LUISS | 2020 | Behavioral | ⚡ ALTA |
| 9 | Value at Risk | Damodaran | var. | Risk | ⚡ ALTA |
| 10 | Monte Carlo Methods in Financial Engineering | Paul Glasserman — Columbia | var. | Risk/Quant | ⚡ ALTA |
| 11 | Stress Test Scenarios | Ryu | var. | Risk | ⚡ ALTA |
| 12 | Limits of Arbitrage | Shleifer & Vishny | var. | Risk/Market | MEDIA |
| 13 | Vanguard's Portfolio Construction Framework | Aliaga-Díaz et al. — Vanguard | var. | Portfolio | ⚡ ALTA |
| 14 | Asset Allocation and Risk Management | Capitolo dedicato | var. | Portfolio | ⚡ ALTA |
| 15 | Common Risk Factors in Stock Returns | Fama & French — JFE | 1993 | Portfolio/Factor | MEDIA |
| 16 | Finance Theory I — Lecture 8: Portfolio Theory | Alex Stomper — MIT Sloan | var. | Portfolio | MEDIA |
| 17 | Portfolio Theory | Testo accademico | var. | Portfolio | MEDIA |
| 18 | UC GEP Investment Policy Statement | University of California | var. | IPS/Disciplina | ⚡ ALTA |
| 19 | Hedge Fund Portfolio Construction | Libro completo | var. | Hedge Fund | ⚡ ALTA |
| 20 | Hedge Fund Replication — Global Macro | Paper accademico | var. | Hedge Fund | ⚡ ALTA |
| 21 | A Primer on Hedge Funds | Paper accademico | var. | Hedge Fund | MEDIA |
| 22 | Hedge Fund Due Diligence as Alpha Source | Paper accademico | var. | Hedge Fund | MEDIA |
| 23 | Hedge Fund Performance, Risk & Capital Formation | Paper accademico | var. | Hedge Fund | MEDIA |
| 24 | Extracting Portable Alphas from L/S HF | Paper accademico | var. | Hedge Fund | MEDIA |
| 25 | Piacentino Paper (HF strutture) | Piacentino | 2013 | Hedge Fund | BASSA |
| 26 | Quantitative Trading | Ernest P. Chan — Wiley | 2009 | Quant | ⚡ ALTA |
| 27 | Understanding Game Theory | Kolokol'tsov & Malafeyev | var. | Quant/Theory | BASSA |
| 28 | Vardarska/Rubandhas Workshop | Workshop slides | var. | Portfolio | MEDIA |
| 29 | wp0408 | Working paper | var. | Risk/Macro | BASSA |

### Skills Operative

| Skill | Funzione | Attivazione |
|-------|----------|-------------|
| `speculative-trading-edge-engine-v2` | Engine principale post-mortem | Default su ogni analisi speculativa |
| `premarket-gap-scanner` | Scanner Fase -1 + Fase 0 | "scan premarket", "fase -1" |
| `small-cap-momentum-scanner` | Scanner swing 15-30gg | "momentum scan", "swing scan" |
| `speculative-continuation-engine` | Continuation setup 5-7gg | "continuation setup" |
| `event-driven-catalyst-analysis` | Analisi catalyst dettagliata | "analisi catalyst" |
| `analisi-equity-trading-investing` | SMC: BOS/CHoCH/FVG | Upload screenshot grafico |
| `skill-analisi-grafico-con-vision-model` | Vision model su chart | `/skill-analisi-grafico` + screenshot |
| `vantaggio-competitivo` | Pattern library | "pattern check" |
| `adaptive-regime-probabilistic-engine` | Monte Carlo + regime | "validazione probabilistica" |
| `conservative-to-dynamic-portfolio` | Portfolio bancario | "portafoglio conservativo" |
| `portfolio-restructuring-strategy` | Recovery da posizioni | "ristrutturazione portafoglio" |

---

## APPENDICE — GLOSSARIO OPERATIVO

| Termine | Definizione |
|---------|-------------|
| **ADV** | Average Daily Volume — volume medio giornaliero |
| **AH** | After Hours — dopo la chiusura del mercato |
| **ATR** | Average True Range — misura volatilità intraday |
| **BOS** | Break of Structure (SMC) — rottura di un livello strutturale chiave |
| **Catalyst TIER 1** | Evento verificato con documentazione legale (8-K, contratto firmato) |
| **CHoCH** | Change of Character (SMC) — inversione della struttura di mercato |
| **CVaR** | Conditional Value at Risk — perdita attesa nel peggior X% di scenari |
| **Disposition Effect** | Tendenza a vendere vincenti troppo presto e tenere perdenti troppo a lungo |
| **FVG** | Fair Value Gap (SMC) — gap di liquidità non riempito |
| **GBM** | Geometric Brownian Motion — modello stocastico del prezzo |
| **HWM** | High Water Mark — massimo storico per il calcolo del performance fee |
| **Kelly Formula** | Formula per il sizing ottimale del capitale |
| **Loss Aversion** | Dolore psicologico per una perdita > piacere per un guadagno equivalente |
| **MOU** | Memorandum of Understanding — accordo non vincolante → TIER 3 |
| **Minsky Moment** | Punto di crollo di un sistema di credito sopravvalutato |
| **Overconfidence** | Sopravvalutazione sistematica della propria accuratezza predittiva |
| **PDUFA** | Prescription Drug User Fee Act — data FDA di decisione su approvazione farmaco |
| **R multiplo** | Rendimento espresso in multipli del rischio iniziale (R/R) |
| **Regime Shift** | Transizione tra stati macroeconomici fondamentalmente diversi |
| **Risk Budget** | Allocazione del rischio totale tra le posizioni |
| **SI** | Short Interest — percentuale del float venduta allo scoperto |
| **SMC** | Smart Money Concepts — framework di analisi tecnica istituzionale |
| **Survivorship Bias** | Errore statistico che include solo i sopravvissuti, non i falliti |
| **Trailing Stop** | Stop loss che si sposta nella direzione del trade vincente |
| **VaR** | Value at Risk — perdita massima attesa con confidenza X% |

---

*Knowledge Base generata il 18 Maggio 2026*  
*Sistema: Speculativo Multi-Layer — IBKR | TradingView | Scanner US Small/Micro-Cap*  
*Universo: NYSE / NASDAQ | Float target: <15M | Catalyst: TIER 1/2 | Orizzonte: 1-15 giorni*
