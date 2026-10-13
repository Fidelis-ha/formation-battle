# Re-Review Mobile-Implementierung (index.html vs. docs/SPEC-mobile.md)

Datum: 2026-10-13 · Referenz: docs/SPEC-mobile.md · Basis: index.html (1504 Zeilen, uncommitted vs. `b8fdebb`)

## Prüfpunkte

### (1) Pointer-Event-Logik Tap-vs-Drag, Ein-Finger-Pan, Pinch — VERIFIZIERT
- `TAP_SLOP = 12` (index.html:720); pointermove markiert `moved` erst ab
  `Math.hypot(dx, dy) > TAP_SLOP` (771), Pan danach relativ mit
  `lx/ly` (772–777), `clampCam()` (775). Tap wird erst bei pointerup
  ausgewertet (787–789) — korrekt gegen "Tap löst zugleich Pan aus".
- Pinch: zweiter Finger verwirft `tapState`, startet Pinch mit
  Mittelpunkt-Anker `pinchState = { d0, wx, wy }` (737–743). Zoom um
  Mittelpunkt: `clamp(zoom * dist/d0, ZOOM_MIN, ZOOM_MAX)` (758) mit
  `ZOOM_MIN/MAX = 0.35/2.2` wie Mausrad (721), danach Weltanker-Pan
  (760–764) und `clampCam()` (765). `d0` wird relativ weitergereicht
  (763) — korrekt. `|| 1` schützt vor Division durch 0 (743, 756).
- Nach Pinch-Abbruch wird verbleibender Finger als `moved: true`-Pan-Anker
  übernommen (790–793) — kein versehentlicher Tap nach Pinch.
- touch-action: none auf #game (index.html:45).

### (2) Tap-Semantik — VERIFIZIERT
`handleTouchTap` (index.html:804–811): eigene Truppe → `G.selected`
(807–808, mit `troopAt(..., touch=true)`, Toleranz 46/26 statt 30/20 —
SPEC-Punkt "44-px-Äquivalent", 599–601); ohne Auswahl → `return` (809);
mit Auswahl → `issueOrder(..., touch=true)` (810), das Feind → Angriff
(676–680), sonst Boden → Marsch (681–685) unterscheidet und bei
`routing` zurückruft (670–675). Kein Befehl ohne Auswahl. ✔

### (3) Keine Doppel-Auslösung — VERIFIZIERT
- canvas `mousedown` (627): `if (isTouchPointer(e)) return;`
- window `mousemove` (646): `if (isTouchPointer(e)) return;`
- canvas `pointerdown` (728): `if (!isTouchPointer(e)) return;`
- `isTouchPointer` = touch|pen (620–622). Trennung ist symmetrisch und
  lückenlos; `e.preventDefault()` bei Touch-pointerdown (745) unterdrückt
  zusätzlich Kompatibilitäts-Maus-Events. Beachte: `window.mouseup`
  (657–660) hat keinen Touch-Guard, setzt aber nur `dragging=false`/
  `G.hover=null` — harmlos (kein Befehl, kein Zoom).

### (4) Long-Press-contextmenu-Block — VERIFIZIERT
- Canvas-Rechtsklick: `e.preventDefault()` (662).
- Document-Level: `if (touchPtrs.size > 0) e.preventDefault()` (815–817)
  blockt Long-Press-Menü, während aktive Touch-Pointer existieren.
- `-webkit-touch-callout: none` + `user-select: none` am body (40–41).

### (5) Sidebar-Karten: pointerdown + mousedown parallel — VERIFIZIERT, kein Doppel
- mousedown (1361–1364) feuert bei Maus (pointerType "mouse" → Guard in
  1367 lässt pointerdown-Handler nicht durch). Touch feuert NUR
  pointerdown (1366–1369, Guard `!== "touch" && !== "pen"` → return).
- Pen: nur pointerdown-Handler aktiv (1370 sichtbar), mousedown via
  canvas-Guard irrelevant — hier DOM-Card: pen erzeugt i. d. R. keine
  kompatiblen mousedown-Events bei pointerdown-capture; auch wenn doch,
  wäre die Aktion idempotent (`G.selected = i` zweimal → gleicher Zustand).
  Kein sichtbarer Doppel-Effekt. `stopPropagation` in beiden (1363, 1368).

### (6) Desktop-Regression — VERIFIZIERT
Diff gegen HEAD: einzige Änderungen an Maus-Code sind
- `troopAt(wx, wy, team)` → `troopAt(wx, wy, team, touch)` (4. Param
  optional, Default `undefined` → alte Werte 30/20, desktop-identisch),
- `issueOrder(sx, sy, touch)` analog (Default-Verhalten unverändert),
- Guard `if (isTouchPointer(e)) return;` in mousedown/mousemove (627, 646)
  — für echte Maus-Pointer no-op.
mousewheel (688–696), keydown (698–710), Mittelklick-Drag (630–633),
Rechtsklick-Befehl (638–640) unverändert. Keine Desktop-Regression
erkennbar.

### (7) touchHint/mouseHint Media-Query — VERIFIZIERT
- Viewport-Meta exakt nach SPEC (33): `width=device-width, initial-scale=1,
  maximum-scale=1, user-scalable=no, viewport-fit=cover`.
- `#touchHint { display: none; }` (100); `@media (max-width: 820px),
  (pointer: coarse)` (102): mouseHint aus, touchHint inline (117–118),
  Sidebar kollabiert nach unten (104–109), Karten ≥44px (`min-height:
  48px`, 110), safe-area-inset-bottom (107). Hinweistexte im Markup
  (164–172) entsprechen SPEC-Wortlaut. Desktop unangetastet.

### (8) DPR-Cap 2 + resize/orientationchange — VERIFIZIERT
- `dpr = Math.min(2, window.devicePixelRatio || 1)` (574).
- `resize` (572–578) + `window.addEventListener("resize", ...)` (579)
  und `addEventListener("orientationchange", ...)` (580). Canvas wird in
  resize mit `vw*dpr` neu bemessen.

### (9) mousemove-Hover auf Touch geblockt — VERIFIZIERT
window-mousemove-Handler returnt für touch/pen (646) → kein
Hover-Ring/kein sinnloses screenToWorld pro Touch-move. Pan-Bewegungen
laufen ausschließlich im pointermove (748–779). Zusätzlich feuert der
Touch-pointerdown kein Hover-Setzen (mousedown-Guard 627).

## Neue Befunde

- **[N1] Schwere: trivial** — `touchPtrs`-Einträge werden bei
  `pointercancel`/`pointerup` bereinigt (783, 796–797) und
  `setPointerCapture` (730) stellt Zustellung sicher; aber: verliert der
  Browser die Pointer-Capture-Bedingung ohne pointercancel (z. B.
  Tabs-Wechsel während eines Pans), bleibt `touchPtrs.size > 0` und der
  document-contextmenu-Block (815–817) bleibt dauerhaft aktiv, bis der
  nächste Touch endet. Kein Spielfehler (Befehle laufen über Tap-Pfad mit
  `G.paused/G.over`-Guards), nur der Rechtsklick-Kontextmenü-Block auf dem
  Dokument wäre bis dahin unterdrückt. Optionaler Härtungspunkt:
  `window.addEventListener("blur", () => { touchPtrs.clear(); tapState =
  null; pinchState = null; })`.
- **[N2] Schwere: trivial** — `touchPtrs.size >= 2 && pinchState` (753):
  wenn ein dritter Finger hinzukommt, nutzt der Pinch trotzdem `[a, b]`
  aus `touchPtrs.values()` (755) — Map-Ordnung ist Einfügereihenfolge,
  d. h. Finger 1+2 werden weiterverwendet, Finger 3 wird ignoriert.
  Deterministisch und korrekt, kein Fix nötig; dokumentiert nur das
  Verhalten bei >2 Fingern.
- **[N3] Schwere: niedrig** — Sidebar-Card-pointerdown (1366) blockiert
  nicht das gleichzeitige Canvas-Tap (Card liegt über Canvas, Canvas
  bekommt den Event nicht — sauber getrennt). Kein Problem, verifiziert
  als dedizierter Hinweis: Tap auf Karte und Tap auf Canvas können nicht
  gleichzeitig auslösen, da die Karte den Event konsumiert und
  `stopPropagation` setzt (1368).

## Fazit
Alle 9 Prüfpunkte VERIFIZIERT. Keine Blocker, keine Majoren. Neue
Befunde sind triviales Härtungspotenzial (N1) bzw. dokumentiertes
Kantenverhalten (N2, N3).
