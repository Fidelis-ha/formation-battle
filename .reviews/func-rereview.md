# RE-REVIEW: Funktion/UX/Code nach Fix-Run 1

**Gegenstand:** `index.html` (1331 Zeilen) — Verifikation F1–F8 + D1–D14
**Datum:** 2026-10-13 · **Vergleichsbasis:** `.reviews/func-ux-code-review.md`
**Ergebnis:** 8/8 Funktion-Fixes VERIFIZIERT. D7 (Leichen) sauber umgesetzt,
keine Doppelzählung, keine toten Akteure. 3 neue MINOR/INFO-Befunde.

---

## Fix-Verifikation

### F1 — Alive-Checks in allen Zielsuchen — VERIFIZIERT
- `updateProjectiles` Einschlag-Suche: `index.html:414` (`if (!s.alive) continue;`), Truppen-Guard `:412` ✅
- `updateCombat` Nahkampf-Zielsuche: `index.html:1062` ✅
- `updateCombat` Fernkampf-Auto-Acquire: `index.html:1086` ✅
- `updateCombat` vBest (Ziel-Soldat in Reichweite): `index.html:1096` ✅
- Alle vier Suchen abgedeckt; zusätzlich Bewegungsziel `:975`, Separation `:1026/:1030`, `soldierGap` `:440/:442`, `troopAt` `:555/:558` (D7-Konsistenz).

### F2 — dest-Reset bei Punkt-Ankunft — VERIFIZIERT
- `index.html:987-990`: `else if (!wantMove.soldiers) { t.dest = null; }` — greift nur bei Punkt-Zielen, Truppen-Ziele bleiben über `targetTroop` geführt. Auto-Acquire (`:929`, Bedingung `!t.dest`) feuert damit wieder; Statusanzeige („Marsch“, `:1206`) fällt auf „Bereit“ zurück.
- Randfall geprüft: Fluchtziel `-80` liegt außerhalb der Cleanup-Grenze `-70` (`:1129-1131`) → geflohene Truppe wird korrekt gezählt, bevor `dest` cleared.

### F3 — Housecarl !isRanged — VERIFIZIERT
- `index.html:180`: `if (atk === "housecarl" && !isRanged) return 1.3;` — Bonus gegen alle Verteidiger im Nahkampf, spec-konumentiert. Nahkampf ruft `counterMult(..., false)` (`:358`), Fernkampf `true` (`:384`) — Hauscarl hat keine Fernattacke, Semantik korrekt.

### F4 — Pause-Guard — VERIFIZIERT
- `index.html:572`: `if (G.paused) return;` als zweiter Guard in canvas-mousedown. Praktisch doppelt abgesichert, da das Pause-Overlay (z-Index 10, inset 0) den Canvas ohnehin verdeckt. Restriktiver als nötig, aber konsistent.

### F5 — Sidebar-Klick-Guard — VERIFIZIERT
- `index.html:1196`: `e.button === 0 && G.playerTroops[i].alive` ✅. Tasten 1–5 hatten den Alive-Check bereits (`:648`).

### F6 — Rally-Marker — VERIFIZIERT
- `index.html:610-614`: Marker nach `rallyTroop` gepusht; `t.dest` ist dort garantiert gesetzt (`rallyTroop` `:294-298` setzt es vorher) → kein Null-Zugriff.

### F7 — endTimer-Cancel — VERIFIZIERT
- `index.html:1169`: `G.endTimer = setTimeout(updateOverlay, 900);`
- `index.html:1274`: `clearTimeout(G.endTimer);` in `init()` —Restart während der 900-ms-Fenster ruft den Overlay-Callback nicht mehr auf. Handle im G-Literal deklariert (`:230`).

### F8 — Kommentare (Ansturm/Burst) — VERIFIZIERT
- `index.html:143` (CHARGE_SPEED-Auslegung), `:256` (Burst truppenweit) ✅

---

## D7 — KRITISCH: Leichen (2,5-s-Silhouetten) — VERIFIZIERT, sauber

Mechanik: `applyDamage` setzt `alive=false` + `deadAt` einmalig (`:343-344`);
`cleanup` filtert erst nach `simTime - 2.5` (`:1117-1121`); Truppe gilt bei
0 **lebenden** Soldaten als vernichtet, bleibt aber mit Leichen im Array
(`:1128`, `:1134-1135`).

| Verbraucher | Leichen-sicher? | Fundstelle |
|---|---|---|
| Treffbar (Nahkampf/Fernkampf/Projektil) | ✅ nein — Alive-Checks in allen 4 Suchen | `:414, :1062, :1086, :1096` |
| **Verlust-Doppelzählung** | ✅ ausgeschlossen — `applyDamage` läuft nur einmal (`hp > 0`-Return `:342` + Ziel-Alive-Checks); `deadCount++`/`losses++` nur im Todes-Zweig `:345-346` | — |
| soldierGap | ✅ überspringt Tote beidseitig | `:440, :442` |
| Slot-Verfolgung / Bewegungsziel | ✅ Tote rücken nicht nach, sind kein Laufziel | `:975, :1016` |
| Separation | ✅ | `:1026, :1030` |
| livingCount | ✅ zählt nur `alive`; genutzt in Sidebar `:1218` und Target-Deselect `:920` | `:1108-1112` |
| checkVictory | ✅ zählt nur `t.alive`; das wird erst bei 0 Lebenden false gesetzt (`:1128`) — Matchende korrekt | `:1164-1165` |
| KI | ✅ filtert `o.alive`; tote Truppen sind kein `foe`, denken nicht mehr | `:456`, aiThink nur für `t.alive` `:1151` |

**Kann eine Truppe mit livingCount 0 noch handeln?** Nein. `cleanup` läuft am
Ende jedes Schritts (`:1157`) und setzt `alive=false`; danach: `updateTroop`
Return `:916`, `updateCombat` Skip `:1051`, aiThink Skip `:1151`. Im
Todes-Schritt selbst können nur bereits abgefeuerte Projektile noch wirken
(akkurat). Rendering der Leichen trotz `!t.alive` korrekt (`drawTroop`
zeichnet Soldaten vor dem Alive-Return, `:806` vs. `:808`). Kein Leck:
Korpsen-Truppen werden spätestens 2,5 s nach der letzten Leiche gespliced.

---

## Regression: moveTarget-Stalemate-Fix — INTAKT

- Bewegung zum **nächstgelegenen lebenden** Feind-Soldaten statt Anker: `:969-980`
- Deadzone-Band (`gap > REACH` → nachrücken, `hold` erst unter `REACH*1.2`): `:947-954`
- F2 greift nur im Punkt-Ziel-Zweig (`!wantMove.soldiers`, `:987`) — override des Stalemate-Fix ausgeschlossen.

---

## Neue Befunde

| # | Schwere | Befund |
|---|---|---|
| N1 | MINOR | **G.hover wird in `init()` nicht zurückgesetzt** (`:1273-1301`). Nach „Neue Schlacht“ zeigt `G.hover` auf eine Truppe des alten Spiels; sofern diese `alive` war, blinkt der Hover-Ring einmal an der Alt-Position, bis die Maus bewegt wird. Rein kosmetisch (Render-Guard `:882` verhindert Schlimmeres). Fix: `G.hover = null;` in `init()`. |
| N2 | MINOR | **Tastatur-Befehle während Pause aktiv** (`:638-649`): Q (Auto-Angriff toggle) und 1–5 (Auswahl) sind pausiert nutzbar, Maus inzwischen nicht mehr (F4). Inkonsistent, aber funktionslos harmlos (Simulation steht). Entweder auch guarden oder Pause-Taktik in der Hinweiszeile dokumentieren. |
| N3 | INFO | **mousemove-Performance**: Jedes Mousemove-Event ruft `screenToWorld` + `troopAt` (`:592-594`) — ~120 Distanzchecks bei vollem Feld. Bei typischen Event-Raten (60–125 Hz) völlig vernachlässigbar; ein Throttle ist optional, keine Handlung nötig. |

### D12-Pause-Restart — geprüft, VERIFIZIERT
`btnPauseRestart` → `init()` (`:1265`); `init` setzt `G.paused=false` (`:1282`),
`clearTimeout(G.endTimer)` (`:1274`), Sidebar wird neu gebaut. Listener hängen
jeweils an frischen DOM-Elementen (innerHTML-Reset) — keine Akkumulation.

### G.hover-Leck — siehe N1 (einziger verbleibender, kosmetischer Rest)

---

## Fazit

Alle gemeldeten Funktion-Fixes korrekt und vollständig umgesetzt; der
frühere KRITISCH-Befund A1 ist inklusive der neuen Leichen-Mechanik (D7)
wasserdicht — keine Doppelzählung, keine handlungsfähigen Geistertruppen,
keine Lecks. Verbleibend: 2 MINOR (N1, N2), 1 INFO (N3). Kein Blocker.
