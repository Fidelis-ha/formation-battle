# TRIPLE-REVIEW: Funktion + Nutzererlebnis + Codequalität

**Gegenstand:** `index.html` (1191 Zeilen) gegen `docs/SPEC-formation-battle.md`
**Datum:** 2026-09-29
**Methode:** Vollständige Codelektüre, SPEC-Mechanik-Abgleich Zeile für Zeile.

**Gesamteindruck:** Solide, spec-nahe Implementierung mit klarer Abschnitts-
struktur und sauberem Objekt-Lifecycle. Ein kritischer Buchhaltungsbug im
Kampfsystem, zwei wichtige Logik-/Auslegungsprobleme, sonst Minor-Niveau.

---

## A. FUNKTION

### A1. KRITISCH — Tote Soldaten werden im selben Simulationsschritt erneut getroffen (Doppelzählung)

- **Fund:** `index.html:944-948` (`updateCombat`, Zielsuche) und
  `index.html:404-408` (`updateProjectiles`, Einschlag-Suche)
- **Problem:** Beide Zielsuchen iterieren `f.soldiers` / `t.soldiers`, **ohne
  `v.alive` / `s.alive` zu prüfen**. Tote Soldaten bleiben bis zum `cleanup()`
  am Ende von `update()` (Zeile 1024) im Array. Trifft Angreifer A einen
  Soldaten tödlich, kann Angreifer B im selben Kampfdurchlauf denselben Leichnam
  treffen: `applyDamage` (Zeile 333-345) läuft erneut durch — `deadCount++`,
  `G.losses[team]++`, erneuter `checkMoraleLosses`-Aufruf.
- **Wirkung:** Verluste und `deadCount` werden überzählt → Moral-Bruch
  (50 %-Schwelle) tritt **früher ein als korrekt**, Endscreen-Statistik ist
  falsch. Bei dichtem Frontgefecht (mehrere Angreifer auf denselben
  Vorderreihen-Soldaten) regelmäßig möglich.
- **Vorschlag:** In beiden Schleifen `if (!v.alive) continue;` ergänzen
  (`updateCombat` Zeile 945, `updateProjectiles` Zeile 406).

### A2. WICHTIG — `t.dest` wird nach Ankunft nie zurückgesetzt → Auto-Angriff dead und falscher Status

- **Fund:** `index.html:861-878` (Bewegung, Ankunft bei `d <= 6` ändert nur die
  Position), `index.html:820` (Auto-Erkennung verlangt `!t.dest`),
  `index.html:1069-1074` (`troopStateText` gibt bei gesetztem `dest` „Marsch“ aus)
- **Problem:** Nach einem Move-Befehl bleibt `dest` dauerhaft gesetzt. Folge:
  1. Der Auto-Acquire-Block (Zeile 820, Bedingung `!t.dest`) feuert für diese
     Truppe nie wieder — Nahkampf-Truppen mit `autoAttack: an` laufen Feinden in
     260 px Umkreis nicht mehr hinterher (nur passives Kämpfen bei direktem
     Kontakt via Zeile 950-956). Inkonsistent zu Truppen ohne vorherigen
     Move-Befehl.
  2. Sidebar zeigt nach Ankunft dauerhaft „Marsch“, obwohl die Truppe steht.
- **Vorschlag:** Nach Bewegungsausführung: `if (d <= 6 && !wantMove.soldiers)
  t.dest = null;` (Truppen-Ziele werden über `targetTroop` geführt, nur
  Punkt-Ziele clearen).

### A3. WICHTIG (Auslegungsfrage) — Housecarl-Counter greift nicht gegen Schützen im Nahkampf

- **Fund:** `index.html:175` — `atk === "housecarl" && !isRanged &&
  !RANGED_TYPES.has(def)` → x1.3
- **Problem:** SPEC Zeile 36: „Housecarl → **alles** Nahkampf: leichter
  Schadensbonus durch Rüstung (x1.3)“. Der Code schließt Archer/Skirmisher als
  Verteidiger aus. Laut SPEC-Tabelle (Zeile 23) brechen Schützen im Nahkampf
  zusammen — der Hauscarl-Bonus sollte dort nach Spezifikation greifen. Die
  Code-Lesart („nur gegen Nahkampf-Typen“) ist eine mögliche, aber engere
  Interpretation als der SPEC-Text.
- **Vorschlag:** Bedingung zu `atk === "housecarl" && !isRanged` ändern
  (Bonus gilt für jeden Verteidiger, solange der Angriff Nahkampf ist) — oder
  die engere Lesart explizit als Kommentar am `counterMult` dokumentieren.

### A4. MINOR — Kavallerie-Ansturm: normales Marschtempo erfüllt die Ansturm-Bedingung bereits

- **Fund:** `index.html:138` (`CHARGE_SPEED = 95`) vs. `index.html:162`
  (Kavallerie `speed: 135`)
- **Problem:** Kavallerie ist mit 135 px/s **immer** über der Ansturm-Schwelle,
  sobald sie sich überhaupt bewegt — auch bei einem simplen Move-Befehl ohne
  Feindkontakt gibt es beim ersten Aufprall den x2.5-Bonus. Die Schwelle
  unterscheidet nicht „Ansturm“ von „Marsch“. Der Verbrauchs-Mechanismus
  (`chargeReady`, Zeile 355-360/883) begrenzt den Effekt, aber die SPEC-Formulierung
  („Bonus nur bei Bewegungsgeschwindigkeit > X **beim Aufprall**“) ist so
  technisch erfüllt, praktisch aber bedeutungslos.
- **Vorschlag:** Entweder Schwelle über Basistempo legen (z. B. 150, erfordert
  dann einen Sprint-/Charge-Modus) oder akzeptieren und im Kommentar
  (`index.html:352-354`) festhalten, dass jeder Bewegte-Kontakt der ersten
  Kavallerie-Salve als Ansturm zählt.

### A5. MINOR — Skirmisher-Burst ist truppenweit, nicht pro Soldat

- **Fund:** `index.html:249` (`burstLeft: 3` an der Truppe), `index.html:377-380`
- **Problem:** SPEC Zeile 37 („erste 3 Würfe x1.5“) ist mehrdeutig. Der Code
  interpretiert: 3 Würfe **pro Truppe** (12 Soldaten schießen, nur die ersten
  3 Projektile der ganzen Truppe sind verstärkt). Alternative Lesart: 3 Würfe
  **pro Soldat** (36 verstärkte Würfe) — das wäre ein deutlich stärkerer Burst.
- **Vorschlag:** Aktuelle Lesart per Kommentar festhalten (`// truppenweit,
  nicht pro Soldat`) oder auf pro-Soldat (`s.burstLeft = 3`) umstellen, falls
  der stärkere Burst gewollt ist.

### A6. MINOR — `setTimeout` für den Ergebnis-Overlay nicht abbrechbar

- **Fund:** `index.html:1036` (`setTimeout(updateOverlay, 900)`)
- **Problem:** Der Timer-Handle wird nicht gespeichert. Praktisch harmlos
  (Neustart ist erst nach Overlay-Anzeige möglich, ESC/P während der 900 ms
  ruft `updateOverlay` zwar vorzeitig auf, zeigt aber korrekt das Ergebnis),
  aber robustheitshalber sollte `init()` einen evtl. hängenden Timer clearen.
- **Vorschlag:** `G.endTimer = setTimeout(...)` in `checkVictory`, in `init()`
  (`index.html:1134`) `clearTimeout(G.endTimer)`.

### A7. Mechanik-Abgleich: erfüllt (ohne Befund)

| SPEC-Punkt | Fundstelle | Status |
|---|---|---|
| 7 Einheitentypen, 10–12 Soldaten/Truppe | `index.html:148-163`, `253-265` | ✅ (alle Zeilen/Spalten 10–12, SPEC fordert 8–12) |
| Spearman→Cavalry x3.0 | `index.html:170` | ✅ |
| Cavalry→Archer/Skirmisher x2.5 | `index.html:171` | ✅ |
| Archer/Skirmisher→Swordsman x1.5 | `index.html:172` | ✅ (gilt Fern- und Nahkampf; passt zu „anfällig gegen Fernkampf“, SPEC Zeile 28) |
| Swordsman→Archer/Skirmisher/Spearman x2.0 | `index.html:173-174` | ✅ |
| Skirmisher-Burst 3× x1.5 | `index.html:249, 377-380` | ✅ (Lesart siehe A5) |
| dmg = base × counter × formation ±15 % | `index.html:306, 363, 412` | ✅, keine weitere Crit-Mechanik |
| Flanken/Rücken x1.5 per Richtungscheck | `index.html:318-325` (Winkel > ~54,5°), angewandt `362` (Nahkampf) und `411` (Projektil) | ✅ |
| Flankenangriff im Nahkampf bricht Moral sofort | `index.html:341-344` | ✅ (nur `isMelee`, korrekt) |
| Moral >50 % Verluste → Flucht; nach Sammeln 70 % | `index.html:242, 287-291, 328-330` | ✅ (streng `>`, passend zu „>50 %“) |
| Flucht zum Kartenrand | `index.html:279-300` | ✅ (nächster Rand, +80 px) |
| Spieler-Rückruf fliehender Truppen | `index.html:588-591` → `rallyTroop` `287-291` | ✅ (Rechtsklick, setzt 70 %-Schwelle) |
| Cavalry-Charge mit Geschwindigkeit + Verbrauch | `index.html:355-360, 883` | ✅ (Nutzwert siehe A4) |
| KI je Typ: Vorrücken / Distanz halten / Flanke / Speere nahe Linie | `index.html:441-506` | ✅; gleiche Daten & Formeln, keine Cheats (AI liest nur `G.troops`) |
| Sieg/Niederlage inkl. Flucht (tot ODER geflohen) | `index.html:994-1003` (Flucht entfernt Truppe) + `1029-1037` | ✅ inkl. Unentschieden-Fall |
| Ergebnis-Screen: Dauer + Verluste je Seite | `index.html:1106-1130` | ✅ (inkl. Gefechten/Geflohene) |
| Fixer 60-fps-Timestep | `index.html:1163-1183` (Akkumulator, `STEP = 1/60`, dt-Clamp 0,25 s) | ✅ korrekt entkoppelt von rAF |
| Kein Truppen-Editor, fixe Aufstellung | `index.html:181-196` | ✅ |

### A8. Speicherlecks: geprüft, keine gefunden

- **Projektile:** konsumierende `keep`-Filterung, Einschläge werden entfernt —
  `index.html:395-423`. Kein Wachstum. ✅
- **Marker:** Lebenszeit-Dekrement + `splice` — `index.html:1004-1007`. ✅
  (Nichtkreis: Dekrement hardcoded `1/60` statt `dt`, siehe C4.)
- **Truppen/Soldaten:** tote Soldaten gefiltert (`index.html:989-993`),
  leere/geflohene Truppen via `splice` entfernt (`index.html:994-1003`). ✅
- **Dangling Refs:** `targetTroop` auf entfernte Truppen wird über das vor dem
  `splice` gesetzte `alive = false` abgefangen (`index.html:811`, `996-999`);
  Angriffs-Marker prüfen `m.troop.alive` vor dem Zeichnen (`index.html:770`);
  `G.selected` wird in `selectedTroop()` gegen `alive` validiert
  (`index.html:628-632`). ✅
- **DOM/Listener:** Window/Canvas-Listener nur einmal registriert;
  Sidebar wird bei `init()` per `innerHTML = ""` neu gebaut
  (`index.html:1046-1067`); `btnRestart`-Listener hängt an einem jeweils
  frischen Element (`index.html:1121-1123`). ✅
- Einziger weicher Punkt: der nicht gecancelte `setTimeout` (A6).

---

## B. NUTZERERLEBNIS

### B1. Steuerung — vollständig und spec-konform ✅

Linksklick-Auswahl (`index.html:561-564`), Rechtsklick Move/Attack inkl.
Ziel-Erkennung (`583-602`), Mausrad-Zoom um den Cursor (`604-612`),
Mittelklick-Drag (`557-560, 570-579`), Q-Toggle (`619-621`), 1–5
(`622-625`), ESC/P-Pause (`616-618`). Alle in der deutschen Hinweiszeile
(`index.html:121-125`) dokumentiert. UI-Texte durchgehend deutsch ✅
(einzelne englische Kommentar-Fragmente siehe C6).

### B2. WICHTIG — Statusanzeige „Marsch“ bleibt nach Ankunft stehen

- **Fund:** `index.html:1069-1074` (in Verbindung mit A2)
- **Problem:** Nach Abschluss eines Move-Befehls zeigt die Karten-Statuszeile
  dauerhaft „Marsch“, obwohl die Truppe steht und kampfbereit ist.
- **Vorschlag:** Durch Fix A2 obsolet (`dest` clearen bei Ankunft).

### B3. MINOR — Rückruf einer fliehenden Truppe ohne visuelles Feedback

- **Fund:** `index.html:588-591` — `issueOrder` kehrt nach `rallyTroop` zurück,
  **ohne** einen Marker zu setzen (Move/Attack setzen welche, Zeile 596/600).
- **Wirkung:** Der Spieler erhält keine Bestätigung, dass der Rückruf
  angenommen wurde; die FLUCHT-Anzeige der Karte springt erst mit dem nächsten
  Sidebar-Update zurück.
- **Vorschlag:** `G.markers.push({ kind: "move", x: t.dest.x, y: t.dest.y, life: 1.2 });` ergänzen.

### B4. MINOR — Befehle und Auswahl während Pause möglich

- **Fund:** `index.html:555-568` — `mousedown` prüft nur `G.over`, nicht
  `G.paused`; Rechtsklick-Befehle und Kartenauswahl sind pausiert möglich.
- **Wirkung:** Kann als Feature (Pause-Taktik) gelten, ist aber inkonsistent
  zum Overlay-Text („P oder ESC zum Fortsetzen“) und nicht dokumentiert.
- **Vorschlag:** Entweder bewusst lassen und in der Hinweiszeile erwähnen,
  oder `if (G.paused) return;` in den Auswahl-/Befehl-Zweigen.

### B5. MINOR — Sidebar: tote Karten sind anklickbar

- **Fund:** `index.html:1061-1063` — `mousedown` setzt `G.selected = i` ohne
  `alive`-Prüfung. `selectedTroop()` fängt es ab (Zeile 628-632), es gibt also
  keinen Funktionsfehler — nur eine toote Auswahl, die z. B. den rot
  markierten Zielring (Zeile 740-746) betrifft (der prüft `alive` ebenfalls).
  Reiner Kosmetik-Befund.
- **Vorschlag:** `if (e.button === 0 && G.playerTroops[i].alive) { ... }`.

### B6. MINOR — „Moral“ in den Truppenkarten ist indirekt

- **Fund:** `index.html:1084-1094` — der Balken (`.mfill`) zeigt den
  Soldatenanteil, Moral nur binär über Status-Text („FLUCHT!“, rote Färbung).
- **Bewertung:** SPEC fordert „Soldatenzahl, Moral“ (Zeile 78). Da Moral im
  Modell binär ist (gefct. oder nicht), ist die Umsetzung vertretbar; der
  Balken ist aber de facto ein Stärke-, kein Moral-Balken.
- **Vorschlag:** Bar-Label klären (z. B. Tooltip „Truppenstärke“) — rein
  dokumentarisch.

### B7. Overlay-Verhalten ✅

Pause-Overlay korrekt (`index.html:1124-1127`), Ergebnis-Overlay mit Dauer,
Verlusten je Seite und Geflohene-Zahlen (`1106-1130`), Neustart-Button
funktional. Kosmetik: ESC/P während der 900 ms-Endverzögerung zeigt das
Ergebnis sofort (siehe A6) — unkritisch.

---

## C. CODEQUALITÄT

### C1. Abschnitts-Struktur ✅

Alle sieben deklarierten Marker vorhanden und in sinnvoller Reihenfolge:
CONFIG (131), ENTITIES (209), COMBAT (302), AI (437), INPUT (508), RENDER
(634), MAIN (801). Der Kopf-Kommentar (Zeile 3-28) stimmt mit der realen
Gliederung überein. Lizenz-Hinweis (MIT), Autor („Kairos für Marc“),
Inspirationsquelle und Eigenständigkeits-Hinweis sind vollständig — SPEC
Zeile 86-88 erfüllt.

### C2. MINOR — Tote Variable `t.id` / `nextTroopId`

- **Fund:** `index.html:228, 234, 1147` — ID wird vergeben und zurückgesetzt,
  aber nirgends gelesen.
- **Vorschlag:** Entfernen oder tatsächlich nutzen (z. B. Debug-Overlay,
  Marker-Referenzierung).

### C3. MINOR — `clamp` gehört nicht in die INPUT-Sektion

- **Fund:** Definition `index.html:536`, Nutzung bereits in AI (Zeile 460,
  461, 478, 479). Zur Laufzeit unkritisch (const ist bis zum ersten Aufruf
  initialisiert), aber die Sektionszugehörigkeit stimmt nicht.
- **Vorschlag:** Nach CONFIG (unter `WORLD`) verschieben.

### C4. MINOR — Marker-Lebenszeit hardcoded statt über `dt`

- **Fund:** `index.html:1005` — `G.markers[i].life -= 1 / 60;` obwohl
  `cleanup()` im Kontext des fixen Timesteps läuft.
- **Vorschlag:** `cleanup(dt)` mit Parameter — robuster gegen spätere
  Refactorings (z. B. variablen Timestep).

### C5. MINOR — `G.result` fehlt im State-Literal

- **Fund:** Erst zur Laufzeit gesetzt (`index.html:1035`, `1144`), nicht im
  `G`-Literal (`index.html:213-226`) deklariert.
- **Vorschlag:** `result: null,` ins Literal aufnehmen (Konsistenz,
  Auffindbarkeit).

### C6. MINOR — dt./engl. Mischmasch in Kommentaren

- **Funde:** „unprotected assault“ (`index.html:172`), „Deadzone“ /
  „Stalemate“ (`index.html:858-859`). Der Rest der Kommentare ist
  durchgängig deutsch.
- **Vorschlag:** „Schutzlos-Schlag“ bzw. „Deadlock/Patt“ — oder als
  Fachbegriffe konsistent markieren. Ebenfalls prüfbar: `keep` (Zeile 396)
  → `uebrig`.

### C7. MINOR — `updateSidebar` frisst 15 `querySelector`-Aufrufe pro Frame

- **Fund:** `index.html:1085-1093` — pro Karte 3 `querySelector` pro Frame
  (60 fps × 5 Karten).
- **Wirkung:** Bei 5 Karten vernachlässigbar, aber unnötig.
- **Vorschlag:** Element-Referenzen einmalig in `buildSidebar()` cachen
  (parallel zu `cardEls`).

### C8. Sonstiges (Beobachtungen, keine Pflicht)

- Doppelte „nächsten Feind-Soldaten suchen“-Loops (Auto-Acquire `index.html:822-825`,
  Gefechtserkennung `886-891`, Zielsuche `941-948`) könnten in eine
  Hilfsfunktion `nearestFoeSoldier(t, maxD)` zusammengeführt werden.
- `ctx.arc(..., 0, 7)` als 2π-Ersatz (mehrere Stellen, z. B. Zeile 652) —
  funktioniert, `Math.PI * 2` wäre selbsterklärender.
- `let base`/`let mult` in `meleeStrike` (Zeile 349-350) könnten `const` sein.
- Namensgebung insgesamt konsistent und sprechend (`routThreshold`,
  `speedSmooth`, `soldierGap`, `formationMult`); keine weiteren toten
  Variablen gefunden (alle `UNITS`-Felder, `G`-Felder und Flags werden
  gelesen).

---

## D. Priorisierte Fix-Liste

| Prio | Befund | Ort | Fix-Aufwand |
|---|---|---|---|
| KRITISCH | A1: Tote Soldaten erneut treffbar → doppelte Verluste/Moral | `index.html:404-408, 944-948` | 2 Zeilen |
| WICHTIG | A2/B2: `dest` nie gecleart → Auto-Angriff tot, „Marsch“-Status | `index.html:873` | 1-2 Zeilen |
| WICHTIG | A3: Housecarl-Bonus vs. Schützen klären/implementieren | `index.html:175` | 1 Zeile oder Kommentar |
| MINOR | B3: Rally-Marker | `index.html:588-591` | 1 Zeile |
| MINOR | A4/A5: Charge-/Burst-Auslegung dokumentieren | `index.html:138, 249` | Kommentar |
| MINOR | A6: endTimer cancellen | `index.html:1036, 1134` | 2 Zeilen |
| MINOR | B4/B5: Pause-/Karten-Klicks absichern | `index.html:555-568, 1061` | je 1 Zeile |
| MINOR | C2-C7: Tote Variable, clamp-Sektion, Marker-dt, G.result, Kommentare, Query-Cache | diverse | Kosmetik |
