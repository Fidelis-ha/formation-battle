# Security-Review — Formation Battle (index.html)

**Reviewer:** glm-5.3 (OpenCode) · **Datum:** 2026-09-29
**Objekt:** `index.html` (1191 Zeilen) — rein clientseitiges Canvas-Spiel, ein Match, kein Server
**Kontext / Bedrohungsmodell:** Lokal oder statisch gehostet, über `file://` lauffähig. Kein Auth, keine sensiblen Daten, keine Nutzerdaten-Persistenz, keine Kommunikation. Angegriffen werden könnte hier real nur: der Spieler selbst (Selbst-DoS, Bug-getriggerte Ressourcen-Limits) oder — falls jemals dynamische Werte in DOM/URL kämen — zukünftige XSS-Flächen.
**Prüfkriterien (Vorgabe):** XSS via innerHTML, Prototyp-Pollution, unsicheres Random, externe Abhängigkeiten (SPEC-Verstoß), Datei-/Netz-Zugriffe, Event-Handler-Injektion, DoS (wachsende Arrays, Endlosschleifen in `update()`), onclick/inline-Handler, URL-Parameter.

---

## Ergebnis auf einen Blick

| Kategorie | Befund |
|---|---|
| KRITISCH | **0** |
| WICHTIG | **0** |
| MINOR | **2** (M1: Marker-Array wächst bei Pause + Rechtsklick-Spam; M2: innerHTML-Muster als zukünftige Pflege-Falle) |
| INFO | 2 (kein CSP-Meta; `Math.random()` — nur Spielfunktion, per Vorgabe irrelevant) |

Die App ist für ihr Bedrohungsmodell **sicher**. Es existiert kein einziger Kanal, über den externe Daten in den DOM, in Objekt-Strukturen, in URLs oder ins Netz gelangen. Alle innerHTML-Nutzungen werden ausschließlich aus hardcodeden Konstanten und internen Zahlen gespeist.

---

## Befunde nach Schwere

### KRITISCH

Keine Befunde.

### WICHTIG

Keine Befunde.

### MINOR

**M1 — `G.markers` wächst unbegrenzt bei Pause + Rechtsklick-Spam (einziges reales DoS-Restrisiko, nur selbst betreffend)**
- **Befund:** Die Lebensdauer der Befehls-Marker wird ausschließlich in `cleanup()` dekrementiert (index.html:1004–1007), und `cleanup()` läuft nur innerhalb von `update()` — das bei Pause nicht ausgeführt wird (index.html:1173–1179). Der `mousedown`-Handler prüft aber nur `G.over`, nicht `G.paused` (index.html:556), und `issueOrder()` (index.html:583) feuert auch im Pausenzustand. Rechtsklick-Spam mit gewählter, lebender Truppe während der Pause lässt `G.markers` damit unbegrenzt wachsen; `render()` iteriert jeden Frame über alle Marker (index.html:763), Speicher und Frametime steigen linear. Ein autoclicker-ähnliches Szenario kann den Tab also verlangsamen — aber nur der Spieler selbst kann es auslösen, es gibt keine Remote-Komponente.
- **Einordnung:** Realistisch MINOR: selbst verschuldet, lokal, behebbar durch Reload. Kein Angriffsvektor von außen.
- **Fix (2 Zeilen):** Entweder in `issueOrder()` bei `G.paused` direkt returnen, oder das Marker-Dekrement aus `cleanup()` in `frame()` verschieben (zeitbasiert statt sim-basiert), oder ein hartes Limit (`if (G.markers.length > 32) G.markers.shift()`).

**M2 — innerHTML-Muster mit Template-Strings: heute statisch sicher, morgen die erste XSS-Fläche**
- **Befund:** Drei Stellen nutzen `innerHTML` mit Interpolation: `buildSidebar` (index.html:1053–1060, `${i + 1}. ${u.name}` + `ICONS[t.type]`), `updateOverlay` (index.html:1112–1121, `${title}`, `${cls}`, `${dur}`, `G.losses[…]`, `G.fled[…]`) und das Pause-Panel (index.html:1125, rein statisch). **Alle** eingesetzten Werte stammen aus den hardcodeden Konstanten `UNITS`/`ICONS` (index.html:148–207) bzw. aus internen Zahlen/Enums (`G.result` ∈ {"win","lose","draw"}, Zähler, Zeitstring). Kein einziger Wert ist von außen beeinflussbar — daher **kein aktuelles XSS**. Das Muster ist trotzdem der erste Hebel, an dem XSS entstünde, wenn später dynamische Werte dazukämen (Truppen-Editor, URL-Parameter, Speicherstände, Mod-Namen).
- **Einordnung:** MINOR (Pflege-Hinweis / zukünftige Angriffsfläche, kein heutiger Impact).
- **Fix (optional):** Für die Overlay-Werte `textContent`/`createElement` nutzen statt String-Interpolation, oder zumindest eine klare Konvention dokumentieren ("in diese Templates dürfen niemals externe Werte"). Die `ICONS`-SVGs könnten einmalig per `DOMParser` geparst und als Knoten eingehängt werden.

### INFO

**I1 — Kein CSP-Meta-Tag.** Bei aktuell null Injection-Vektoren ist das reine Defense-in-Depth-Kosmetik. Ein `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:">` würde die Datei aber gegen zukünftige Versehen härten (und das Fehlen externer Loads für immer festschreiben — passend zur SPEC).

**I2 — `Math.random()` vielfach genutzt** (index.html:250, 259, 306, 373–374, 648 ff.): Streuung, Cooldowns, Terrain-Deko, Flankenseite — ausschließlich Spielbalance, wie in der Vorgabe als irrelevant eingestuft. Kein Secret, kein Token, kein Loot- determinism-Angriffsszenario.

---

## Geprüfte Vektoren im Detail

**1. XSS via innerHTML mit dynamischen Werten — nicht verwundbar.**
Vollständige innerHTML-Inventur: index.html:1053 (`buildSidebar`), 1112 (`updateOverlay` Sieg/Niederlage), 1125 (Pause-Panel). Datenfluss-Analyse aller interpolierten Werte:
- `u.name`, `t.type`, `ICONS[t.type]`: hardcodete Konstanten (index.html:148–207); `t.type` entsteht ausschließlich aus `DEPLOY`-Literalen (index.html:181–196).
- `i + 1`: Schleifenindex. `dur`: aus `G.simTime` (interne Sim-Uhr) formatierter Zahlenstring. `G.losses[0/1]`, `G.fled[0/1]`: interne Zähler, ausschließlich durch `applyDamage`/`cleanup` mit numerischen Inkrements verändert (index.html:338, 1000).
- `title`/`cls`: abgeleitet aus `G.result`, das nur die Literale `"win"`, `"lose"`, `"draw"` annimmt (index.html:1035).
Kein Pfad von Außenwelt (URL, Storage, Netz, Zwischenablage, Drag&Drop) in eines dieser Felder. Kein `document.write`, kein `eval`, kein `new Function`, kein string-basiertes `setTimeout` (`setTimeout(updateOverlay, 900)` nutzt eine Funktionsreferenz, index.html:1036).

**2. Prototyp-Pollution — nicht vorhanden.** Kein dynamischer Objekt-Merge, kein `Object.assign` auf externen Daten, keine aus Input abgeleiteten Property-Keys. Die einzigen "dynamischen" Indizierungen sind `G.losses[victimTroop.team]` / `G.fled[t.team]` (index.html:338, 1000) — `team` ist durchgehend die Literale 0/1 aus `makeTroop`-Aufrufen. `UNITS[t.type]`, `TEAM_COLOR[t.team]` etc. analog: Literal-gefüttert. Kein `__proto__`/`constructor`-Pfad existiert.

**3. Unsichere Random-Nutzung — irrelevant (siehe I2).**

**4. Externe Abhängigkeiten — KEINE, SPEC-konform.** Mechanische Suche nach `src=`, `href=`, `fetch`, `XMLHttpRequest`, `WebSocket`, CDN-Domains (unpkg/jsdelivr/cdn), `import(`: null Treffer. Der einzige `https://`-String im Dokument ist die itch.io-Referenz im Lizenz-/Herkunftskommentar (index.html:11) — Text, kein Lademodul. CSS und JS vollständig inline; Icons sind handgeschriebene Inline-SVG-Strings statt einer Icon-CDN. Erfüllt „keine externen Abhängigkeiten" (SPEC Z. 14).

**5. Datei-/Netz-Zugriffe — keine.** Kein `fetch`/XHR/WebSocket/EventSource, kein `Worker`/`ServiceWorker`, kein `postMessage`, kein `navigator.*`-Zugriff, kein Filesystem-/Drag&Drop-Handling. Kein `localStorage`/`sessionStorage`/`indexedDB`/`document.cookie` — das Spiel hält ausdrücklich keinen Zustand vor (SPEC „keine User-Input-Persistenz" bestätigt). Einzige Ressource: eigener Speicher (offscreen Terrain-Canvas, 2600×1700 px ≈ 17,7 MB RGBA, **einmalig** beim Laden erstellt und bei Restart wiederverwendet — index.html:638, 1185; kein Leak).

**6. Event-Handler-Injektion — nicht vorhanden.** Im HTML-Markup existiert kein einziges `onclick`/`onload`/`onerror`-Attribut. Sämtliche Listener werden per `addEventListener` mit Funktionsreferenzen registriert (resize, mousedown/mousemove/mouseup, contextmenu, wheel mit `passive: false` für Zoom, keydown, Karten-mousedown, Restart-click). Keine Handler-Strings, keine Inline-JS-Attribute → keine Injektionsfläche.

**7. DoS-Risiken — geprüft, ein MINOR (M1) gefunden, sonst sauber:**
- **`G.projectiles`:** strikt bereinigt — Einschlag entfernt das Projektil, `keep`-Filter in jedem Schritt (index.html:395–422). Projektile bewegen sich mit fester Geschwindigkeit auf einen festen Einschlagpunkt zu und erreichen ihn garantiert in endlicher Zeit → Array ist nach oben durch Feuerrate × Flugzeit begrenzt (real zweistellig).
- **`G.troops`:** startet fix bei 10 (2×5 aus `DEPLOY`, kein Spawn zur Laufzeit) und kann nur schrumpfen (`cleanup` entfernt tote/geflochene, index.html:994–1003). Kein Wachstum möglich.
- **`G.markers`:** einziges wachsendes Array — siehe M1 (nur bei Pause entkoppelt).
- **Endlosschleifen in `update()`:** Der Fixed-Timestep-Loop `while (acc >= STEP)` ist durch `dt`-Clamp auf 0,25 s begrenzt → max. 15 Sim-Schritte pro Frame, auch nach Tab-Wechsel (index.html:1170–1179). Die `while`-Schleifen in `angleDiff` (index.html:309–314) terminieren sicher, da die Eingaben aus `Math.atan2` im Bereich [-π, π] liegen. Keine `while(true)`, keine rekur- siven Aufrufe in der Simulation.
- **Rechenlast:** `soldierGap`, die Separations- und die Combat-Loops sind O(Soldaten²) bis O(Soldaten³) (index.html:426–435, 909–924, 928–985) — bei fix max. 10 Truppen × ≤12 Soldaten (~120 Soldaten gesamt) unkritisch und nicht von außen skalierbar (keine Möglichkeit, Einheiten zu erzeugen).
- **Speicher bei Restart:** `init()` setzt alle Arrays zurück (index.html:1134–1147); alte Truppen/Karten werden dem GC übergeben, alte Karten-DOM-Elemente samt Listener mit `sidebar.innerHTML = ""` verworfen — keine Listener-akkumulation, kein Leak über Matches hinweg.

**8. onclick-/Inline-Handler — keine** (siehe Vektor 6).

**9. URL-Parameter-Nutzung — keine.** Kein Zugriff auf `location`, `URLSearchParams`, `document.URL`, `document.referrer` oder `window.name` im gesamten Skript. Die App ist vollständig eingabeparameter-frei; `file://`- wie Host-Betrieb verhalten sich identisch.

---

## Positive Sicherheitsbeobachtungen

- `"use strict"` aktiv (index.html:130) — keine impliziten Globals, keine `arguments.callee`-Eskapaden.
- Keine Mutation von `window`/document-Globals durch Spiellogik; aller Zustand gekapselt in `G` und Truppen-Objekten.
- `contextmenu` und `wheel` sauber mit `preventDefault` gehandhabt; `keydown` hört ohne Default-Unterdrückung (kein Browser-Hijack).
- `setTimeout` ausschließlich mit Funktionsreferenz; `checkVictory` gegen Doppel-Auslösung gesichert (`if (G.over) return`, index.html:1030).
- Keine `Function`/`eval`/string-to-code-Pfade irgendwo im Dokument.

## Fazit

Für ein lokal laufendes, serverloses Canvas-Spiel ohne Auth und ohne sensible Daten ist die Angriffsfläche **praktisch null**: Es gibt schlicht keinen Eingabekanal außer Maus/Tastatur, und deren Daten fließen ausschließlich in numerische Spiellogik — nie in DOM-Strings, Objekt-Keys, URLs oder Netz-Calls. Die beiden MINOR-Befunde sind ein konsistenter Selbst-DoS-Randfall bei Pause (M1, 2-Zeilen-Fix) und ein innerHTML-Muster, das nur bei zukünftigen Feature-Erweiterungen mit dynamischen Werten relevant würde (M2). KRITISCH wäre hier nichts angemessen — es existiert kein Befund mit echtem Auswirkungspotenzial über den eigenen Browser-Tab hinaus.
