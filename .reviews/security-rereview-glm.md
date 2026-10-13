# Security-Re-Review — Formation Battle (index.html)

**Reviewer:** glm-5.3 (OpenCode) · **Datum:** 2026-10-13
**Vorheriger Bericht:** `.reviews/security-review-glm.md` (2026-09-29) · **Fix-Quelle:** `.reviews/fix-run-1.log` (F1–F8, D1–D14)
**Objekt:** `index.html` (1331 Zeilen, Stand nach Fix-Lauf; JS-Syntax per `node --check` verifiziert)

---

## Ergebnis auf einen Blick

| Prüfpunkt | Ergebnis |
|---|---|
| (1) CSP-Meta-Tag (D14) | **VERIFIZIERT** — syntaktisch korrekt, kompatibel mit allen verwendeten Features |
| (2) Neue sicherheitsrelevante Stellen durch die Fixes | **NEIN** — keine neuen Vektoren; M1 (Marker-Wachstum bei Pause) bestätigt behoben |

KRITISCH: **0** · WICHTIG: **0** · MINOR: **0** neu

---

## (1) CSP — VERIFIZIERT

Tag (index.html:32):
`default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:`

- **Syntax:** Valide — Direktiven semikolongetrennt, Keywords korrekt einfach gequoted. Keine in `<meta>` unzulässigen Direktiven (`frame-ancestors`, `report-uri`, `sandbox`) verwendet.
- **Inline-Script** (index.html:134): vom klassischen Inline-`<script>` ohne Nonce/Hash → `script-src 'unsafe-inline'` deckt es ab. ✓
- **Inline-Style:** `<style>`-Block (Z. 34) sowie Style-Attribute im injizierten Pause-Overlay (Z. 1261–1263, `style="font-size:28px"` etc.) → von `style-src 'unsafe-inline'` abgedeckt; CSSOM-Zugriffe (`fill.style.width`, Z. 1225) unterliegen ohnehin keiner CSP-Sperre. ✓
- **Inline-SVG via innerHTML** (ICONS, Z. 1186–1187): wird als DOM-Knoten geparst, kein Ressourcen-Load; die SVG-Strings enthalten kein `href`/`xlink:href`/`<use>` und keine externen Referenzen. CSP-relevant wäre nur ein Load innerhalb des SVG — existiert nicht. ✓
- **Canvas:** `getContext("2d")` und `drawImage` des offscreen Terrain-Canvas (Z. 853) fallen unter keine CSP-Ressourcen-Direktive; kein `new Image()`, keine Bild-URLs im Spiel. `img-src data:` ist damit aktuell ungenutzt (harmlos, Defense-in-Depth). ✓
- **file://-Betrieb:** Meta-CSP wird von Chrome/Firefox/Edge auch für `file://`-Dokumente angewandt; die Policy blockiert nichts, was die Seite selbst zum Laufen braucht (kein `connect-src`-Bedarf — null Netz-Zugriffe; System-Fonts statt `@font-face`, kein `url()`/`@import` im CSS). ✓
- **Wirksamkeit:** `default-src 'none'` blockiert künftig jegliches externe Laden (fetch, Medien, Frames, Worker, Manifest) — verankert den SPEC-Punkt „keine externen Abhängigkeiten" dauerhaft. ✓

Optionale Härtung (kein Befund): `script-src 'unsafe-inline'` ließe sich langfristig durch einen sha256-Hash des Script-Blocks ersetzen; bei zero externen Eingabekanälen (verifiziert: kein `location`/Storage/Netz/PostMessage) heute nicht nötig. Kosmetisch: ein `/favicon.ico`-Request würde von der Policy geblockt (Browser-Standard-Icon).

## (2) Neue Befunde — NEIN

Basis: Vollinventur aller Fix-Stellen laut fix-run-1.log gegen die aktuelle Datei.

- **F4 Pausen-Guard (Z. 570–572):** `mousedown` returnet bei `G.over` **und** `G.paused`. `issueOrder()` ist ausschließlich über diesen Handler erreichbar; alle vier `G.markers.push`-Stellen (Z. 424 in `updateProjectiles` — läuft nur im `update()`-Loop, der in Pause nicht ausgeführt wird, Z. 1313; Z. 613/620/624 in `issueOrder` — in Pause unerreichbar) sind damit dicht. **M1 (unbegrenztes Marker-Wachstum bei Pause + Rechtsklick-Spam) bestätigt behoben.**
- **Neue innerHTML-Stellen:** weiterhin genau 4 (Z. 1180, 1186, 1247, 1260). Alle interpolierten Werte weiterhin Literale bzw. interne Zahlen/Enums (`u.name`, `ICONS[t.type]`, `G.result` ∈ {win,lose,draw}, Zähler, Zeitstring, `TYPE_SHORT`-Literals) — null externe Eingabe. Das Pause-Panel (Z. 1260) interpoliert nur Konstanten. M2-Muster unverändert statisch sicher.
- **Neue Event-Handler:** `btnRestart`/`btnPauseRestart` werden per `addEventListener` verdrahtet (Z. 1258, 1265); da `panel.innerHTML` vor jedem Neu-Aufbau die alten Knoten samt Listener verwirft, gibt es keine Listener-Akkumulation über Matches hinweg (`init()` setzt zusätzlich alle Arrays zurück, `clearTimeout(G.endTimer)` verhindert doppelte Overlays). Keine Inline-Handler-Attribute im Markup.
- **Mousemove-Hover-Logik (D4):** `G.hover` ist reine Lese-Erkennung (`troopAt`, alive-gefiltert), fließt nur ins Canvas-Rendering (Z. 882–887), nie in DOM-Strings; Aufräumen bei `mouseup`/`mouseleave` korrekt. Kein Injektions- oder DoS-Potenzial (O(10 Truppen) pro mousemove, auch in Pause unkritisch — es entsteht nichts Persistierendes).
- **Neue Marker-Arten:** Rally-Move-Marker (Z. 613) über `issueOrder` → pause-blockiert; `hit`-Einschlag-Marker (Z. 424, life 0.3 s) nur im Sim-Loop, durch Einschlagrate begrenzt und in `cleanup()` dissipiert. Kein wachsendes Array ohne Bounds.
- **Vektor-Mechanik erneut geprüft:** kein `eval`/`new Function`/`document.write`, kein string-basiertes `setTimeout`, kein `location`/`URLSearchParams`/Storage/`postMessage`, kein `fetch`/XHR/WebSocket/Worker, kein Netz/Direktzugriff — unverändert null externe Eingabekanäle. Prototyp-Pollution weiterhin ausgeschlossen (nur Literal-Indizierungen, kein Merge).

---

## Fazit

**CSP VERIFIZIERT, neue Befunde: NEIN.** Der Fix-Lauf hat die beiden MINOR-Punkte des Erstreviews geschlossen (M1 Pausen-Guard, D14 CSP als I1) und keine neue Angriffsfläche geschaffen. Sicherheitsstatus unverändert: für das Bedrohungsmodell (serverloses, eingabefreies Canvas-Spiel) praktisch null Angriffsfläche, jetzt mit CSP als Dauer-Absicherung gegen zukünftige versehentliche externe Loads.
