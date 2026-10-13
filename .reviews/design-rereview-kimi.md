# Design-RE-REVIEW — Formation Battle (Fix-Verifikation)

**Reviewer:** kimi-k3 (OpenCode) · **Datum:** 2026-10-13
**Vorheriger Bericht:** `.reviews/design-review-kimi.md` (2026-09-29)
**Fix-Quelle:** `.reviews/fix-run-1.log` (14 Design/Security-Fixes D1–D14 + 8 Funktions-Fixes F1–F8)
**Geprüfte Datei:** `index.html` (1331 Zeilen; JS-Syntax `node --check`: OK, 1194 Zeilen)
**Verifikationsmethode:** Codezeilen-Prüfung **plus** Live-Verifikation in headless Chromium (Playwright, `file://`, 1280×578) mit Pixel-Messung der Screenshots. Evidenz-Shots: `.reviews/shots/rereview-1-start.png`, `rereview-2-hpbalken-zoom072.png`, `rereview-3-gefecht-zoom072.png`, `rereview-4-fluchtfahne.png`. Laufzeitfehler: **0** (console/pageerror leer).

---

## 1) Verifikation je Fix

### K1 — Feld-Banner (Spielernummer vs. KI-Kürzel) → **VERIFIZIERT**
- `TYPE_SHORT`-Tabelle mit Kürzeln für alle 7 Typen: index.html:710–714 (`archer:"BO"`, `skirmisher:"PL"`, `housecarl:"HK"`, `cavalry:"KA"` …).
- Banner in `drawTroop`: index.html:810–827. Spieler: `String(G.playerTroops.indexOf(t) + 1)` (Z. 813–814) — identische Reihenfolge wie Sidebar-Karten (Z. 1189: `${i + 1}. ${u.name}`) und Tasten 1–5 (Z. 646–648) → Zuordnung Feld ↔ Karte ↔ Taste konsistent. KI: Typ-Kürzel (Z. 815). Teamfarben-Füllung, dunkler Rahmen, weiße 9px-Ziffer, Zoom-Schwelle `> 0.5` (Z. 812), unterdrückt bei Flucht (sinnvoll, dort greift W5).
- **Pixel-Beweis (Zoom 0.72):** Bannerbox + weiße Ziffer „2" exakt an den berechneten Bildschirmkoordinaten über der Hauscarls-Truppe (`rereview-2`, Box ~12×9 px, Ziffer als `ffffff`-Pixel messbar). Start-Zoom 0.9 > 0.5 → Banner von Beginn an sichtbar.

### K2 — Startkamera auf eigene Armee → **VERIFIZIERT**
- index.html:1286: `G.cam = { x: 560, y: 850, zoom: 0.9 };` in `init()` — deckt die komplette Spieler-Aufstellung (x 380–640, y 480–1440) ab; bei 1280×578 Viewport: sichtbarer Ausschnitt x 560±711, y 850±321 → alle 5 Spielertruppen im Bild, KI weiterhin off-screen (korrekt, kein Spoiler nötig).
- **Pixel-Beweis (`rereview-1`):** 1721 blaue Soldaten-Pixel im ersten Frame, 0 rote — der alte Befund „leere Wiese" ist behoben.

### W1 — Projektile + Einschlag → **TEILWEISE / PROBLEM (P1)**
- Projektile selbst: index.html:892–905 — `lineWidth 2.5`, Längen 14/18, hellere Farben `#f0e6c8`/`#e0d0a5`, zusätzlicher Kopf-Punkt `#fff6d8` r=2. **Pixel-Beweis (`rereview-3`, Zoom 0.72):** 855 pfeilfarbene + 20 kopffarbene Pixel im aktiven Gefecht — Pfeile sind jetzt klar vorhanden. **VERIFIZIERT.**
- Einschlag-Marker: Erzeugung index.html:424 (`kind:"hit", life: 0.3`), Zeichnung index.html:866–869 (`#fff2c0`, r=2.2). **PROBLEM:** Die Marker-Schleife setzt `ctx.globalAlpha = Math.min(1, m.life)` (index.html:857) — mit `life: 0.3` startet der Punkt bei **max. 30 % Deckkraft** und fällt von dort weiter ab. Pixel-Messung: trotz 8 Frames mit aktiven Hit-Markern (per `page.evaluate` gezählt) nur **2 Pixel** in `#fff2c0` nachweisbar → der Einschlag ist praktisch unsichtbar. Der alte W1-Teilbefund „kein Einschlag-Feedback" besteht damit faktisch fort.
- **Fix-Vorschlag (1 Zeile):** Alpha relativ zur Marker-Art normieren, z. B. in Z. 866–869 vor dem Zeichnen `ctx.globalAlpha = Math.min(1, m.life / 0.3);` — oder `life: 1.0` setzen und Radius stattdessen schrumpfen lassen.

### W2 — Auswahlring + Hover-Feedback → **VERIFIZIERT**
- Auswahlring: index.html:797–805 — `#9fc2ff` (helles Teamblau), `lineWidth 2.5`, Dash [6,5], Radius 66, gezeichnet **vor** den Soldaten (Ring liegt unter der Formation, nicht darüber → bleibt als Kreis lesbar).
- Hover: `G.hover`-Feld (index.html:227), `mousemove` setzt `G.hover = troopAt(w.x, w.y, 0)` (Z. 592–594), Aufräumen bei `mouseup`/`mouseleave` (Z. 597–601), Darstellung als schwacher Ring alpha 0.4, gleiche Geometrie wie Auswahlring (Z. 881–888), vor den Truppen gezeichnet (Z. 881 vor 890).
- `troopAt` ist gegen Leichen/tote Truppen abgesichert (Z. 555–558), Hover schlägt also nicht auf Gefallene an.

### W3 — Teamfarbe konstant + Mini-HP-Balken → **VERIFIZIERT**
- Konstante Farbe: index.html:739–740 (`ctx.fillStyle = TEAM_COLOR[t.team];`), kein `hpFrac` mehr im Code. Kavallerie-Reiter jetzt `TEAM_DARK` (Z. 746) — Unterscheidung Pferd/Reiter bleibt, Teamfarbe dominant.
- **Pixel-Beweis:** Soldat mit 30 % HP rendert den Körper weiterhin als reines `#4f8fe0` (gemessen in `rereview-2`, Körper-Zeilen 284–293) — Abdunklung eliminiert.
- Mini-HP-Balken: index.html:787–794 — nur bei `s.hp < s.maxHp`, schwarzer Träger `rgba(0,0,0,0.55)` 10×2 Welt-px + Füllung `10*frac` in Grün/Gelb/Rot je nach Fraktion, positioniert bei `s.y + u.radius + 3` (unter dem Soldaten).
- **Pixel-Beweis (Zoom 0.72, Hauscarl radius 7):** Balken auf Bildschirm-Zeilen 296–297 unmittelbar unter dem Körper (Körper endet Zeile 293), ~7 px breit inkl. dunklem Träger, gelbe Füllung (~2 px bei 30 % HP) messbar. Details zur Sichtbarkeit → Abschnitt 2a.

### W5 — Weiße Fluchtfahne → **VERIFIZIERT**
- index.html:829–840: Stab `#e8e4d8` von `t.y-8` bis `t.y-34`, Fahne `#f4f4ec` als 14-px-Dreieck nach rechts, gezeichnet nach dem `if (!t.alive) return;` (Z. 808) → erscheint über dem Anker jeder lebenden, fliehenden Truppe beider Teams; Banner wird im Gegenzug bei Flucht unterdrückt (Z. 812) — keine Überlagerung.
- **Pixel-Beweis (`rereview-4`, Zoom 1.0):** weiße Fahnen-Pixel (44) mit horizontalem Verlauf 11→7→4 px Breite = exakt die Dreiecksform, über dem Anker. Position → Abschnitt 2b.

### K3 — Leichen-Silhouetten (2,5 s) → **VERIFIZIERT** (Teil b); Teil a bleibt offen
- `victim.deadAt = G.simTime` in `applyDamage` (index.html:344); Silhouette in `drawSoldier` (Z. 722–729): dunkle Ellipse `rgba(18,22,14,0.6)`, rotiert in `t.facing`, früher `return` → keine Waffe/HP-Balken für Tote.
- `cleanup()` (Z. 1114–1141): Filter `s.alive || s.deadAt > expire` mit `expire = simTime - 2.5` (Z. 1117–1121); Truppentod erst bei **0 lebenden** Soldaten (Z. 1128); Truppe bleibt mit Leichen bis zum Verwehen im Array (Z. 1134–1135).
- Konsistenz: `livingCount()` (Z. 1107–1112) in Zielabwahl (Z. 920) und Sidebar-Zähler (Z. 1218–1220); Slot-Nachrücken (Z. 1016), Separation (Z. 1026–1030), `soldierGap` (Z. 439–442), alle Zielsuchen (Z. 414, 558, 975, 1062, 1086, 1096) überspringen Gefallene → Leichen blockieren weder Bewegung noch Zielwahl, bleiben aber 2,5 s sichtbar liegen. `checkVictory` zählt nur `t.alive` (Z. 1164–1165). **Pixel-Beweis:** dunkle Silhouetten-Flächen im Gefechtshot messbar.
- **Offen (bewusst nicht Teil des Fix-Laufs):** K3(a) — stärkere Slot-Bindung hinterer Reihen im Nahkontakt — ist **nicht** umgesetzt (`move`-Faktor Z. 1014 und `engagedWith`-Ausrichtung Z. 1006–1007 unverändert). Formationsgeometrie zerfällt im Gefecht weiterhin; siehe „Verbleibende Befunde".

### M1 — Hilfeleiste umbrechbar → **VERIFIZIERT**
- index.html:80–88: `display:flex; flex-wrap:wrap; white-space:normal`, Media-Queries 1100 px/800 px (11/10 px Schrift).

### M2 — Befehlsmarker-Farbsemantik → **VERIFIZIERT**
- Bewegung `#9fc2ff` hellblau (index.html:859), Angriff `#ffb347` orange (Z. 864). Rot bleibt exklusiv Feind: Zielring der eigenen Truppe auf Feind bewusst `#ff5b5b` (Z. 877) — konsistent, da er eine Feindtruppe markiert, keinen Befehlstyp. Grün ist damit nur noch Moral-Balken.

### M3 — Kartenbegrenzung → **VERIFIZIERT**
- index.html:678–681: `strokeRect` um die Welt, `lineWidth 120` zentriert auf der Kante → ~60 px dunkelgrünes Band (`rgba(24,34,16,0.55)`) innen. Dezent, aber bei Zoom 0.35 sichtbar.

### M4 — Statuslabels → **VERIFIZIERT**
- index.html:65: `.card .state { font-size: 12px; color: #c4d2b4; }` (vorher 10 px/`#a7b598`).

### M5 — Neustart im Pause-Overlay → **VERIFIZIERT**
- index.html:1259–1265: Button `btnPauseRestart` → `init()`. Kombiniert mit F7 (`clearTimeout(G.endTimer)`, Z. 1274) kein Timer-Leck beim Neustart aus der Pause.

### M6 — Deko-Freihaltung um Aufstellungszonen → **VERIFIZIERT**
- index.html:682–697: `clearOfDeploys` prüft alle 10 Deploy-Punkte, Radius 200 px, greift für Felsen (Z. 689) und Bäume (Z. 697).

### (Zusatz) D14 — CSP-Meta → **VERIFIZIERT**
- index.html:32: `default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:` — Spiel läuft damit fehlerfrei (0 Console-Errors im Live-Test).

---

## 2) Antworten auf die zwei offenen visuellen Fragen

### a) Mini-HP-Balken bei Zoom 0.72 — gezeichnet? sichtbar?
**Ja, sie werden gezeichnet** (Pixel-nachgewiesen unter verwundeten Soldaten, Lage `s.y + radius + 3`, schwarzer Träger + farbige Füllung).
**Sichtbarkeit: grenzwertig.** Rechnung: 10×2 Welt-px × 0.72 = **7,2 × 1,44 Bildschirm-px**; der Soldatenkörper (radius 6–7) misst dort ~9–10 px Durchmesser — der Balken ist also ~70 % der Körperbreite, aber nur ~1,5 px hoch. Die farbige Füllung ist bei 30 % Rest-HP nur ~2 px breit; Antialiasing auf den Bruch-Koordinaten verwässert sie zusätzlich (gemessen `#bca750` statt `#e0c35c`). Praktisch: der dunkle Träger macht den Balken als „Tick unter dem Soldaten" erkennbar, die **Ablesbarkeit des Füllstands leidet** bei 0.72 spürbar; ab Start-Zoom 0.9 (10×2 → 9×1,8 px) ist er gut lesbar. Empfehlung (optional, 1 Zeile): Höhe auf 3 Welt-px erhöhen (Z. 791/793: `…, 10, 3)` bzw. `10 * frac, 3)`) oder Höhe/Länge mit `1/G.cam.zoom` leicht kompensieren.

### b) Weiße Fluchtfahne über dem Anker — korrekt?
**Ja.** Stab verläuft exakt vertikal durch `t.x` von `t.y-8` bis `t.y-34`, Fahne sitzt oben (t.y-34 → t.y-26, 14 px nach rechts), gezeichnet nach allen Soldaten der Truppe → liegt **über** Formation und Anker, nicht verdeckt. Pixel-Beweis in `rereview-4`: Dreiecksverlauf (11/7/4 px) an der erwarteten Position über der fliehenden Truppe. Einzige Einschränkung: der Stab hat dieselbe Farbe wie die Waffen-Silhouetten (`#e8e4d8`) — bei dichtem Gedränge kann er mit einer Waffe verschmelzen; die Fahne selbst (`#f4f4ec`) ist jedoch unverwechselbar.

---

## 3) Icon-Farbkonsistenz der Sidebar

**In der aktuellen Datei: konsistent — kein Befund reproduzierbar.**
- CSS: `.card .icon { color: #9fc2ff; }` (index.html:55) gilt für **alle** Karten; jedes SVG nutzt `stroke="currentColor"` und `fill="none"` (index.html:204–212) — es gibt keinerlei typabhängige Farbquelle im Code.
- **Pixel-Beweis (`rereview-1`, Icon-Spalte x=14–52):** dominante Icon-Farbe `#9fc2ff` (279 px) plus `#7fb2ff` (144 px = Rahmen der selektierten Karte 1, kein Icon). **Keine** grünen oder rotbraunen Pixel in der Icon-Spalte.
- Erklärung der Wahrnehmung „Kavallerie grün / Bogenschützen rotbraun": mit hoher Wahrscheinlichkeit Farbdurchscheinen **benachbarter** Elemente — direkt unter jedem Icon liegt der grüne Moral-Balken (`#7fc47f`, Z. 63) bzw. bei gebrochener Moral der rote Balken/rote „FLUCHT!"-Text (`#d95f5f`/`#ff8b8b`, Z. 64/66), alternativ stammen die Eindrücke aus den alten Screenshots (vor dem Fix). Optionaler Schönheits-Fix, falls die Koppelung stört: Icons teamneutral halten (ist der Fall) und den Moral-Balken farblich vom Icon abrücken (z. B. schmaler Abstand/Divider) — nicht nötig.

---

## 4) Neue Probleme & verbleibende Befunde

### Neue Probleme (durch diesen Re-Review gefunden)

- **P1 — Einschlag-Marker unsichtbar (Alpha-Bug, W1-Nachweis fehlt):** index.html:424 setzt `life: 0.3`, aber index.html:857 dämpft mit `globalAlpha = Math.min(1, m.life)` → max. 30 % Deckkraft von Frame 1 an. Pixel-messen: nur 2 Treffer-Pixel trotz 8 aktiver Marker-Frames. → Fix: Alpha normieren (`m.life / 0.3`) oder `life: 1.0` mit schrumpfendem Radius. (Schweregrad: mittel — der W1-Fix „Einschlag" ist funktional da, visuell aber wirkungslos.)
- **P2 — Banner/Pfahl überlappt die eigene Formation (kosmetisch):** Der Anker liegt *innerhalb* der Formation (z. B. Hauscarls 2×5: Soldat auf Slot col=2/row=0 steht exakt auf dem Anker, weitere bei y±24). Pfahl (t.y-8 → t.y-30) und Box übermalen daher eigene Soldaten (in `rereview-2` schneidet die Bannerbox den Soldaten über dem Anker). Die weiße Ziffer bleibt lesbar (Pixel-verifiziert), aber das Banner steht nicht „über der Truppe", sondern mittendrin. → Optional: Banner an die Formationsoberkante setzen (z. B. `t.y - 30 - (u.rows ? 0 : 0)` ersetzen durch Offset `-maxSoldierDist-14` über `slotPos`-Extent) oder Banner-Hintergrund halbtransparent dunkel statt Teamfarbe, damit er sich vom Körperblau abhebt. (Schweregrad: niedrig.)
- **P3 — Hover-State wird bei Restart/Pause nicht zurückgesetzt (trivial):** `init()` resettet `G.selected`, aber nicht `G.hover` (index.html:1273–1301); `mousemove` aktualisiert Hover auch bei `G.paused`/`G.over` (Z. 586–596 — dort fehlt der Guard, den `mousedown` in Z. 572 hat). Folge: ein schwacher Hover-Ring kann über dem Pause-Overlay liegen bzw. nach Restart kurz an alter Position auftauchen. → 1-Zeilen-Fix: `G.hover = null;` in `init()` + Guard `if (G.paused || G.over) { G.hover = null; return; }` im mousemove-Zweig. (Schweregrad: trivial.)

### Verbleibende Befunde aus dem Erst-Review (bewusst nicht im Fix-Lauf)

- **R1 — W4 (Trefferblitz auf Soldaten, Kavallerie-Staubspur, Schadenszahlen bei Countern): nicht umgesetzt.** Einziges Treffer-Feedback ist der (durch P1 unsichtbare) Projektil-Einschlagspunkt; Nahkampf-Treffer und Ansturm haben weiterhin **kein** visuelles Feedback. Counter-Kernmechanik bleibt unsichtbar.
- **R2 — K3(a) Formationsbindung im Nahkampf: nicht umgesetzt.** Slot-Verfolgung (index.html:1014) und Separation (Z. 1024–1041) unverändert; Front löst sich im Gefecht weiterhin auf, nur die Leichen (Teil b) machen die Verluste jetzt lesbar. Der Befund „Wirrwarr statt Reihen" ist abgemildert, nicht behoben.

---

## Fazit

| Fix | Status |
|---|---|
| K1 Banner (Nr./Kürzel) | ✅ VERIFIZIERT (Code + Pixel) |
| K2 Startkamera | ✅ VERIFIZIERT (Code + Pixel) |
| W1 Projektile | ✅ VERIFIZIERT (Code + Pixel) |
| W1 Einschlag | ❌ PROBLEM P1 (Alpha-Bug, Z. 424/857) |
| W2 Auswahlring + Hover | ✅ VERIFIZIERT |
| W3 Teamfarbe konstant + HP-Balken | ✅ VERIFIZIERT (Code + Pixel) |
| W5 Fluchtfahne | ✅ VERIFIZIERT (Code + Pixel) |
| K3 Leichen-Silhouetten | ✅ VERIFIZIERT (Teil b); Teil a offen (R2) |
| M1–M6 | ✅ alle VERIFIZIERT |
| D14 CSP | ✅ VERIFIZIERT |

**13 von 14 Fix-Stellen sauber umgesetzt und nachgewiesen; 1 Fix (W1-Einschlag) wegen Alpha-Bug faktisch wirkungslos.** Dazu 3 neue kleine Befunde (P1–P3, davon nur P1 sichtbar relevant) und 2 bekannte Restposten (W4, K3a). Empfohlene Minimal-Nachbesserung: 3 Ein-Zeilen-Fixes (P1 Alpha, P3 init-Reset, optional HP-Balken-Höhe 3 px).
