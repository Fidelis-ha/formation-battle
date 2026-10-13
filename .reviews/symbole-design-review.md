# Design-Review — Einheitensymbole (Sidebar-Icons + Feld-Silhouetten)

**Datum:** 2026-10-13 · **Reviewer:** Design-Review (code- und evidenzbasiert)
**Quellen:** `docs/SPEC-symbole.md` (Vorgabe), `.reviews/symbole-shot-descriptions.md`
(neutrale Screenshot-Beschreibungen von Kairos, inkl. Pixel-Proben),
`.reviews/shots/{7-sidebar-icons,8-feld-symbole,10-detail-kavallerie,11-detail-speere}.png`
(Dateipfade; Bilder selbst nicht ausgewertet), `index.html`
(ICONS Z. 248–256, drawSoldier Z. 887–1008, CSS Z. 61/111, Banner Z. 1025–1040).

**Methode:** Codezeilen-Prüfung + Screen-Pixel-Rechnung (Weltmaße × Zoom) +
die neutralen Beobachtungen aus den Shot-Beschreibungen. Die PNGs wurden nicht
direkt gelesen; alle bildbezogenen Aussagen stützen sich auf die Kairos-Beschreibungen
(z. B. Pixelprobe: 736 dunkle Pixel im 60×60-Fenster bei Zoom 3 = Silhouetten
werden gerendert).

---

## Kurzfazit — Antwort auf die Leitfrage

> „Sind die 7 Einheiten bei SPIEL-Zoom (0.7–1.3) auf dem Feld und in der Sidebar
> auf einen Blick unterscheidbar?"

| Kanal | Antwort | Begründung |
|---|---|---|
| **Sidebar-Icons** | **Fast** — 3 von 5 gezeigten Icons eindeutig (Bogen, Axt, Pferd), aber **Speer ↔ Schwert nicht sicher** (von Kairos selbst bei 1,6-fach skalierten Karten, also ~48 px, als schwer unterscheidbar notiert; real: 30 px Desktop / 24 px Mobile) | Beobachtung Shot 7 + Icon-Geometrie (s. S1) |
| **Feld-Silhouetten** | **Nein** — zuverlässig unterscheidbar sind nur **Bogenschütze** (einzige Kurvenform) und **Kavallerie** (Größe/längliche Form), bedingt **Hauscarl** (Blob am Stielende). **Infantry ↔ Swordsman praktisch identisch**, **Spearman ↔ Skirmisher** nur über Länge schwach getrennt | Shot 8 (Zoom 1.3): „keine Typunterscheidung erkennbar (Kreis-mit-Strich-Impression)" + Rechnung unten (F1/F2) |

Wichtige Einordnung: Die **Identifikation auf dem Feld wird heute faktisch vom
Banner** (Truppennummer / TYPE_SHORT-Kürzel, Z. 1025–1040, ab zoom > 0.5)
**getragen** — das ist Lesen, nicht „auf einen Blick", und es fällt unter
Zoom 0.5 komplett weg (Clamp-Minimum ist 0.35, Z. 692). Die SPEC-Zielvorgabe
„Silhouette trägt die Unterscheidung" ist auf dem Feld derzeit nicht erreicht.

---

## Screen-Pixel-Rechnung (Grundlage aller Feld-Befunde)

Weltmaße aus dem Code, multipliziert mit dem Zoom (CSS-px):

| Element | Welt-px | z=0.7 | z=0.9 | z=1.3 |
|---|---|---|---|---|
| Körper-⌀ Standard (r=6) | 12 | 8.4 | 10.8 | 15.6 |
| Körper-⌀ Hauscarl (r=7) | 14 | 9.8 | 12.6 | 18.2 |
| Kavallerie gezeichnet (r=10, Ellipse 28×20) | 20–28 | 14–20 | 18–25 | 26–36 |
| Waffen-lineWidth 2.4 (Z. 936) | — | **1.7** | 2.2 | 3.1 |
| Infantry-Schwert (Länge ≈ 8.6, Z. 963) | 8.6 | 6.0 | 7.7 | 11.2 |
| Swordsman-Klinge (Sehne ≈ 12.8, Z. 957–958) | 12.8 | 9.0 | 11.5 | 16.6 |
| Spearman-Speer (Z. 951–952) | ≈ 21 | 14.7 | 18.9 | 27.3 |
| Skirmisher-Spieß (Z. 946–947) | ≈ 13 | 9.1 | 11.7 | 16.9 |
| Bogen (Bogen-⌀ 12 + Sehne, Z. 941–942) | 12 | 8.4 | 10.8 | 15.6 |
| Formation Abstand lateral/tief (Z. 323–324) | 24 / 27 | 16.8 / 18.9 | 21.6 / 24.3 | 31.2 / 35.1 |

Kontext: Im Nahkampf rücken Feinde bis auf `REACH` 22 bzw. Separation 13.2
Welt-px (Z. 185, 1237) — **dichter als der Formationabstand 24**. Waffenstriche
überkreuzen also regelmäßig fremde Körper; und weil jede Truppe eigenes `facing`
hat, sind **Winkel-Unterschiede zwischen Typen kein verlässlicher Kanal**.

Kontraste (Luminanz, grob): Waffe `#1c2016` auf blauem Körper ≈ 9:1 (gut),
auf rotem Körper ≈ 5.6:1 (ok), auf Gras `#4d6b3a` ≈ 2.9:1, auf dunklen
Grasflecken `#33512a` ≈ 2.2:1 (**schlecht für 1.7-px-Linien**).

---

## Befunde — FELD (drawSoldier, Z. 887–1008)

### KRITISCH

- **F1 — infantry ↔ swordsman sind bei Spielzoom dieselbe Gestalt.**
  Beide sind ein kurzer dunkler Diagonalstrich mit Parier-Querstrich. Die
  einzigen Unterschiede: Krümmung der Swordsman-Klinge (Kurvenmittelpunkt
  weicht nur ≈ 1.1 Welt-px von der Sehne ab → **< 1 Screen-px bei z=0.7**) und
  Länge 6.0 vs. 9.0 Screen-px. Unter Rotation, Überlappung und 1.7-px-Strichbreite
  mit Antialiasing liegt das unter der Wahrnehmungsschwelle. Auch als
  Aggregat-Muster (12 parallele Striche pro Truppe) sehen beide gleich aus.
  SPEC fordert explizit „erkennbar anders als infantry" (SPEC-symbole.md Z. 31)
  — **nicht erfüllt bei Spielzoom.**

- **F2 — Der unterscheidende Waffenteil verschwindet auf dunklem Terrain.**
  Der Typ-Diskriminator ist der über den Körper hinausragende Waffenabschnitt
  (Länge, Axtkopf, Bogen). Genau dieser Teil liegt auf Gras (`#4d6b3a` /
  `#33512a`, Z. 838/868) mit nur 2.2–2.9:1 Kontrast bei 1.7 Screen-px Breite
  (z=0.7) — Antialiasing verwäscht den Rest. Das erklärt exakt die
  Kairos-Beobachtung in Shot 8: sichtbar bleibt nur „Kreis mit Strich"
  (= der On-Body-Anteil der Waffe). Die Pixelprobe (Silhouetten werden
  gerendert) und die Wahrnehmung (keine Typen lesbar) widersprechen sich
  also nicht — **gerendert ≠ lesbar**.

### WICHTIG

- **F3 — spearman ↔ skirmisher nur über die Länge getrennt.**
  Bei z=0.7: 14.7 vs. 9.1 Screen-px, beide diagonal mit kleinem Spitzen-Knick.
  Der Winkel-Unterschied (≈ 17° vs. ≈ 42°) ist wertlos, weil `facing` alles
  dreht. Der Schild-Punkt des Spearman (⌀ 5.2 Welt → 3.6 px bei 0.7) liegt
  *im* Körperinnern und hilft nur bei ruhiger Nahsicht. Einzeln nebeneinander
  gerade noch trennbar, im Gefechtsgewimmel nicht. Einzig das Aggregat
  (12 lange parallele Speere = „Hecke") rettet den Spearman auf Truppenebene
  teilweise.

- **F4 — Kein LOD: volle Detailtiefe wird bei kleinem Zoom zu Matsch.**
  drawSoldier zeichnet bei z=0.7 denselben Pfadsatz wie bei z=3.0: Parier,
  Sehne, Spitzen-Knick, Schild-Punkt — alles Elemente von 1–4 Screen-px,
  die sich gegenseitig und mit den Nachbarkörpern überlagern. Detailtiefe
  ohne Mindestgröße **senkt** die Lesbarkeit (visuelles Rauschen), statt sie
  zu erhöhen. Es fehlt die von der Review-Frage nahegelegte LOD-Stufe
  (ab zoom < 0.8 stark vereinfachte, typische Umrisse).

- **F5 — Kavallerie-Größenvorteil: rechnerisch ausreichend, im Spielzoom-Shot
  nicht separat belegt.** +3 auf r=7 → Körper-⌀ 14 vs. 8.4 Screen-px bei z=0.7
  (1.67×, weit über der ~10–15 %-Weber-Schwelle), dazu längliche Ellipse +
  Kopf/Hals + Reiter-Punkt (Z. 914–928). Pixel-belegt bei Zoom 2.2–3
  (Shot 10). In Shot 8 (z=1.3) wurde Kavallerie nicht gesondert verifiziert.
  Risiko klein, aber: Lanze (Z. 972–973) sieht aus wie ein Spearman-Speer —
  wenn die Pferdekontur im Gewimmel untergeht, bleibt „Speer-Impression".
  → Verifikationslücke, kein Code-Mangel.

### MINOR

- **F6 — Skirmisher: SPEC-Wortlaut „zum Wurf angesetzter Arm" nicht
  dargestellt** (nur Spieß + Spitze, Z. 946–947). Kosmetisch; der Arm wäre
  bei Spielzoom ohnehin unsichtbar — ggf. SPEC-Text anpassen statt Code.
- **F7 — Gefallenen-Ellipse der Kavallerie (u.radius+2 = 9, Z. 894) ist kleiner
  als der lebende Körper (r=10, Ellipse 28×20).** Reine Konsistenzfrage.

---

## Befunde — SIDEBAR (ICONS Z. 248–256, CSS Z. 61/111)

### KRITISCH

- **S1 — Speer (spearman) ↔ Schwert (infantry) bei realer Größe nicht sicher
  unterscheidbar.** Kairos notiert die Verwechslung bereits bei 1,6-fach
  skalierten Karten (~48 px Icon!): „beide lange dünne Diagonale, Unterschied
  (Spitze vs. Parierstange) schwer erkennbar". Code-Analyse stützt das: beim
  spearman-Icon dominiert der gefüllte Kreis (r=6.2 = halbes Icon), der Speer
  ist nur ein ~9 Einheiten langer, ~2 Einheiten dünner Spleiß am Kreisrand
  (bei 30 px: ~11 × 2.5 px); beim infantry-Icon trägt die Parierstange
  (11 Einheiten breit → 13.75 px) die Form, die Klinge ist ein schmaler
  Vertikalstreifen. Bei **30 px Desktop und 24 px Mobile** (Z. 61/111)
  verschärft sich das. SPEC-Ziel „auf einen Blick bei 16–24 px" ist für dieses
  Paar **verfehlt**. (Bogen, Axt, Pferdekopf: von Kairos als eindeutig
  bestätigt.)

### WICHTIG

- **S2 — SPEC-Prüfmaßstab 16–24 px wurde nie getestet.** Shot 7 nutzt 1,6-fach
  skalierte Karten (~48 px); die kleinste reale Darstellung (24 px Mobile,
  Z. 111) und das SPEC-Band 16–24 px sind unbelegt. Wenn S1 bei 48 px schon
  auffällt, ist bei 24 px mit weiteren Ausfällen zu rechnen → muss nach
  etwaigen Icon-Fixes bei 24 **und** 16 px per Screenshot verifiziert werden.

### MINOR

- **S3 — Nur 5 der 7 Icons erscheinen je in der Sidebar.** Das DEPLOY des
  Spielers enthält kein swordsman/skirmisher (Z. 231–236); deren Icons
  (Z. 250, 254) sind in situ unüberprüfbar. Für künftige Reviews: Debug-
  Ansicht/Testseite mit allen 7 Icons.
- **S4 — Inkonsistenz zum SPEC-Füllgebot:** skirmisher-Handschlaufe und
  archer-Sehne sind stroke-only (`fill="none"`, Z. 249–250). SPEC verlangt
  zwar nur „nicht **nur** stroke" (formal erfüllt), aber die Schlaufe
  (stroke-width 1.4) verschwindet bei 16 px faktisch.

---

## Priorisierte Maßnahmenliste

### P1 — KRITISCH beheben (zuerst)

1. **Waffen-Kontrast-Halo (F2).** Waffenpfad zweimal stroken: zuerst hell
   (`rgba(232,228,216,0.8)`, lineWidth 4.2 Welt), dann dunkel `#1c2016` 2.4.
   Der dunkle Silhouetten-Charakter auf dem Team-Körper bleibt (SPEC-konform),
   aber der überstehende Waffenteil löst sich vom dunklen Gras. Ort:
   Z. 934–977 (Pfad einmal aufbauen, zweimal stroken). Aufwand: ~3 Zeilen.
2. **LOD-Stufen in drawSoldier (F4).** Eine Zeile Stufenlogik, z. B.
   `const lod = G.cam.zoom < 0.55 ? 2 : (G.cam.zoom < 0.85 ? 1 : 0);`
   - **lod 1 (< 0.85):** lineWidth 3.2, nur die **eine Primärform** pro Typ:
     archer = Bogenbogen (r 7, ohne Sehne/Pfeil), spearman = Speer volle Länge,
     swordsman = dicke gebogene Klinge (gefüllt, s. P1.3), infantry = gerade
     Klinge, housecarl = Stiel + Axtkopf-Blob, skirmisher = kurzer dicker
     Spieß, cavalry = unverändert (Form trägt). Sekundärstriche (Parier,
     Sehne, Spitzen-Knick, Schild-Punkt) entfallen.
   - **lod 2 (< 0.55):** nur noch Körper + extremes Merkmal (Bogen / lange
     Linie / Blob / Ellipse) — hier trägt ohnehin das Banner ab 0.5 nicht
     mehr, also umso wichtiger.
   Aufwand: überschaubar, komplett lokal im switch (Z. 939–996).
3. **swordsman als gefüllte, breit gebogene Klinge (F1).** Statt quad-
   Strich (Z. 957–959): gefülltes Polygon, Basisbreite ~3 Welt-px → Spitze ~1,
   deutliche Krümmung (Kontrollpunkt 3–4 Welt-px aus der Sehne, nicht 1.1).
   infantry bleibt dünne gerade Linie mit Parier. Damit: **Füllung vs. Linie**
   als harter Formkanal, bei jedem Zoom robust. Sidebar-swordsman (geschwungen,
   Z. 254) und Feld-Silhouette stimmen dann auch konzeptionell überein.
4. **Sidebar-Icon spearman neu gewichten (S1).** Speer über die **volle
   Icon-Diagonale** (z. B. (4,20.5) → (20,4.5)), Schaft ~2.6 Einheiten dick,
   Spitze größer; Schild-Kreis etwas kleiner (r ≈ 5.5) und so platziert, dass
   der Speer ihn **kreuzt** („Speer auf Schild", nicht „Kreis mit Stummel").
   Zusätzlich infantry-Parierstange auf 12 Einheiten verbreitern, damit der
   Orientierungskontrast (45°-Diagonale vs. Vertikale mit Querbar) maximal wird.
   Danach Pflicht-Verifikation bei 24 px und 16 px (S2).

### P2 — WICHTIG (danach)

5. **Zoom-kompensierte Strichbreite (F4-Flankierung).**
   `ctx.lineWidth = Math.max(2.4, 2.0 / G.cam.zoom)` (Z. 936) → mindestens
   ~2.0 Screen-px bei z=0.7 statt 1.7; mindert AA-Verwaschung in lod 0.
6. **Radius als zusätzlicher Unterscheidungskanal (F3/F5).** Verifiziert
   risikofrei: `u.radius` wird **nur** in drawSoldier + HP-Balken-Offset
   verwendet (Z. 894–1006); Kampf/Separation laufen über `REACH`-Konstanten
   (Z. 185, 1237), Slots über fixe 24/27 (Z. 323–324). Vorschlag:
   archer/skirmisher 5.5, infantry/swordsman 6, spearman 6.5, housecarl 7.5,
   cavalry unverändert +3 (→ 10.5). Lateral-Abstand 24 lässt ⌀ 15 locker zu;
   HP-Balken folgt automatisch. Größenstaffel = Zoom-unabhängiger Kanal.
7. **spearman ↔ skirmisher schärfen (F3).** Schild-Punkt r 2.6 → 3.2 und an
   den Körperrand (z. B. (−2,−4)); skirmisher-Spieß kürzen (Ende x=10 statt 12)
   und optional zweiten kurzen Spieß-Stummel dahinter (Bündel-Eindruck).
8. **F5-Verifikationslücke schließen:** Shot bei z=0.7 mit Kavallerie im
   Nahkampf-Gemenge aufnehmen und Größen-/Formwahrnehmung prüfen (gehört in
   die Screenshot-Suite, nicht in den Code).

### P3 — MINOR (bei Gelegenheit)

9. **F6/SPEC-Abgleich:** entweder skirmisher-Arm andeuten (1 kurzer Strich)
   oder SPEC-Text „angesetzer Arm" → „kurzer Wurfspeer vorn" korrigieren.
10. **F7:** Gefallenen-Ellipse für cavalry an gezeichnetes r angleichen.
11. **S3:** Debug-Ansicht aller 7 Icons (z. B. `?icons=1`), damit swordsman/
    skirmisher-Icons überhaupt reviewbar sind.
12. **S4:** skirmisher-Schlaufe füllen statt stroken (16-px-Festigkeit).
13. **Screenshot-Suite erweitern:** Sidebar in 1.0× (30 px) und 24 px sowie
    16 px; Feld bei z=0.7 und z=0.35 (Banner-freie Zone unter 0.5!) — bisher
    liegen nur 1.6× bzw. z=1.3/2.2–3.0 vor.

---

## Verifikationsplan (nach Umsetzung von P1)

1. Sidebar-Screenshot unskaliert (30 px) + simulierte 24/16 px: alle Paare,
   speziell spearman↔infantry, spearman↔swordsman, skirmisher↔infantry.
2. Feld-Screenshots bei z=0.7 / 0.9 / 1.3, jeweils Marsch **und** Nahkampf-
   Gemenge; Checkliste: alle 7 Typen ohne Banner-Lektüre benennbar?
   (Banner ggf. testweise ausblenden, um die Silhouetten isoliert zu prüfen.)
3. Pixelprobe wie bisher (dunkle Pixel) **plus** Kontrastprobe des Halo auf
   Grasflecken `#33512a`.
4. Regression: HP-Balken-Position (folgt u.radius), Banner ab 0.5, keine
   Sim-Änderungen (REACH/Separation unangetastet).

## Bewertung SPEC-Konformität (Ist)

| SPEC-Forderung | Status |
|---|---|
| Icons gefüllt, currentColor, 7 Embleme laut Tabelle | ✅ (Z. 248–256; Schlaufe/Sehne stroke → S4) |
| Formen bei kleiner Größe deutlich unterscheidbar | ❌ spearman↔infantry (S1); 16–24 px ungetestet (S2) |
| Feld: Kreis-Körper in Teamfarbe + typspezifische Waffe | ✅ umgesetzt, ❌ Wirkung bei Spielzoom (F1–F4) |
| swordsman erkennbar anders als infantry | ❌ auf dem Feld (F1), ✅ in der Sidebar |
| cavalry größer (+3) + Pferdekontur | ✅ Code, ⏳ Spielzoom-Nachweis offen (F5) |
| Teamfarbe konstant, Silhouetten dunkel | ✅ — aber Kontrast zum Terrain unterschätzt (F2) |
| HP-Balken & Banner unangetastet | ✅ |
| Keine Mechanik-/Balance-Änderung | ✅ |
