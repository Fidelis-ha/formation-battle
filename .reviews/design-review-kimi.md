# Design-Review — Formation Battle (Web-App)

**Reviewer:** kimi-k3 (OpenCode) · **Datum:** 2026-09-29
**Leitfrage:** Wirkt die Schlachtdarstellung klar, lesbar und stimmig nach der SPEC (Formationen sichtbar, Auswahl erkennbar, Kampfbezug verständlich)?
**Quellen:** `docs/SPEC-formation-battle.md`, `.reviews/shot-descriptions.md`, `index.html` (CSS + RENDER, Zeilenbezug unten)

---

## Gesamteindruck

Die App trifft die SPEC in den Grundfesten: klare blau/rot-Teamfarben, deutschsprachige UI, Truppenkarten-Sidebar mit Auswahl, Match-Zeit oben, Ergebnis-Screen, Hilfeleiste. Der Kampfbezug auf dem Feld ist jedoch in mehreren Kernpunkten schwach: **die Zuordnung Sidebar-Karte ↔ Feldformation ist nicht gegeben** (keine Nummern auf dem Feld), **die Startkamera zeigt keine einzige Armee**, und **Formationen verlieren im Gefecht ihre sichtbare Geometrie** — drei Dinge, die die SPEC explizit fordert ("Geometrie sichtbar", "Auswahl hervorgehoben", "Anti-Übersichtlichkeits-Fehler vermeiden"). Dadurch wirkt die Schlacht auf dem Feld unklarer, als es die Mechanik hergibt.

**Antwort auf die Leitfrage:** Teilweise. Farbsemantik und UI-Rahmen sind stimmig; Feldlesbarkeit (Formationen, Auswahl, Truppen-Zuordnung) und Start-Einstieg sind die Schwachstellen.

---

## Befunde nach Schwere

### KRITISCH

**K1 — Keine Feld-Sidebar-Zuordnung: Truppen-Nummern/Banner fehlen auf dem Feld**
- **Befund:** Die Sidebar nummeriert die Karten ("1. Speerkämpfer" … "5. Kavallerie", index.html:1056) und die Tasten 1–5 wählen danach aus (index.html:622–625). Auf dem Feld selbst hat eine Formation **keinerlei Kennzeichnung** — `drawTroop` (index.html:738–748) zeichnet nur Soldaten + einen Auswahlring für die eine gewählte Truppe. Im Gefecht (shot 2) sind zwei rote Keile sichtbar, aber es ist unmöglich zu sagen, welcher Feind-Keil welchem Typ entspricht, und für die eigenen (off-screen/verdeckten) Truppen fehlt jeglicher Anker. Der Beobachter notiert: "Zuordnung Feldformation zu Sidebar-Karte unklar."
- **SPEC-Bezug:** "Formation aus 8–12 Einzelsoldaten in Reihen (Geometrie sichtbar!)" (Z. 42), "Anti-Übersichtlichkeits-Fehler vermeiden" (Z. 79).
- **Änderungsvorschlag:** In `drawTroop` (index.html:738) über dem Anker `t.x/t.y` ein kleines Banner zeichnen: farbiges Team-Fähnchen mit der Truppen-Nummer (1–5) für Spielertruppen bzw. einem Typ-Kürzel (z. B. "SP", "HK") für KI-Truppen. Optional nur ab einem Zoom-Schwellwert einblenden, damit es bei 0.35-Zoom nicht flackert. Das ist ~10 Zeilen Canvas-Code und schließt die Lücke Feld↔Sidebar vollständig.

**K2 — Startkamera zeigt keine Armee (erster Eindruck = leere Wiese)**
- **Befund:** `init()` setzt die Kamera auf Kartenmitte (index.html:1146: `G.cam = { x: WORLD.w/2, y: WORLD.h/2, zoom: 0.72 }`). Bei Welt 2600×1700 und Viewport 1280×578 deckt Zoom 0.72 nur ~1778×803 Weltpixel um die Mitte ab — die Spieler-Aufstellung bei x≈380–640 und die KI bei x≈1960–2170 liegen **beide außerhalb**. Shot 1 bestätigt: "Keine Einheiten im sichtbaren Bereich." Der Spieler startet mit einer leeren Grasfläche und muss erst suchen.
- **SPEC-Bezug:** Ziel "selbstlaufendes Spiel" + Darstellung "Farben/Flaggen klar unterscheidbar" (Z. 74) — davon sieht der Spieler beim Start nichts.
- **Änderungsvorschlag:** Startkamera auf die eigene Armee zentrieren, z. B. `G.cam = { x: 560, y: 850, zoom: 0.9 }` in `init()` (index.html:1146). Optional beim ersten Befehl (erster Rechtsklick in `issueOrder`, index.html:583) sanft auf die Kartenmitte ziehen — aber der erste Frame muss die eigenen Truppen zeigen.

**K3 — Formationsgeometrie zerfällt im Gefecht sichtbar (Wirrwarr statt Reihen)**
- **Befund:** Im Gefecht wirken die Formationen laut Beobachter "als lockere Keile, nicht als klare Reihen" und teils als "diagonale/keilförmige Ordnung" (shot 2). Ursache im Code: Sobald Nahkontakt besteht, dreht `t.facing` auf den Feind-Anker (index.html:892–893), die Slot-Verfolgung läuft mit halber Kraft weiter (index.html:900), und die gegnerische Separation drückt Soldaten auseinander (index.html:909–924). Zusätzlich verschwinden gefallene Soldaten sofort (cleanup, index.html:988–993) — Lücken in der Front sind nicht lesbar, die Reihe "wächst nach" ohne visuelle Logik.
- **SPEC-Bezug:** "Geometrie sichtbar!" (Z. 42), "Soldaten kämpfen positionsgenau, vorderste Reihe zuerst" (Z. 47–48).
- **Änderungsvorschlag:** (a) Im Zustand `engagedWith` die Slot-Verfolgung für hintere Reihen (row ≥ 1) stärker binden, damit die Truppe als Block liest; (b) tote Soldaten nicht sofort entfernen, sondern 2–3 s als dunkle "Gefallenen"-Silhouette liegen lassen (z. B. `s.deadAt`-Zeitstempel, im cleanup zeitverzögert filtern) — das macht Verluste und die schrumpfende Front auf dem Feld ablesbar. Beides erhöht die Schlacht-Lesbarkeit erheblich.

---

### WICHTIG

**W1 — Projektile praktisch unsichtbar (Fernkampf ohne visuelles Feedback)**
- **Befund:** Shot 2 (aktives Gefecht mit Bogenschützen/Plänklern im Spiel): "KEINE Projektile erkennbar." Code-Seite: Pfeile sind 9 Weltpixel lange, 1.6 px breite Linien in blassem `#e9dfc0` (index.html:786–796). Bei Zoom 0.72 sind das ~6.5×1.2 Bildschirmpixel — gegen das strukturierte dunkelgrüne Terrain nahezu kontrastfrei. Flugzeit bei 340 px/s über 260 px Reichweite: ~0.76 s, also ~45 Frames — genug Zeit zum Sehen, wenn man sie denn sieht.
- **SPEC-Bezug:** Fernkampf ist Kernmechanik (Archer/Skirmisher + Counter-Multiplikatoren, Z. 23–24, 33–34); ohne sichtbare Geschosse fehlt der Kampfbezug.
- **Änderungsvorschlag:** Projektile vergrößern + kontrastieren: `lineWidth: 2.5`, Länge arrow 14 / javelin 18, plus heller Kopfpunkt (`ctx.arc(p.x, p.y, 2)` in Weiß/Gelb). Alternativ/ergänzend: minimale Zoom-Kompensation `len / G.cam.zoom`. Zusätzlich Einschlag-Feedback (kleiner Staub-/Funken-Punkt beim Treffer in `updateProjectiles`, index.html:400–414).

**W2 — Auswahl auf dem Feld kaum wahrnehmbar; kein Hover-Feedback**
- **Befund:** Die gewählte Truppe erhält einen weiß gestrichelten Kreis mit Radius 66, `lineWidth: 1.5` (index.html:740–746) — bei Zoom 0.72 ein ~1-px-dünner gestrichelter Ring, der laut Beobachter im Gefechtshot **nicht sichtbar** ist ("Kein sichtbarer Auswahl-Ring/Marker"). Die Sidebar zeigt die Auswahl zwar klar (hellblaue Umrandung, `.card.sel` index.html:52), aber ohne Feld-Zuordnung (K1) hilft das nicht beim Klicken. Es gibt außerdem keinerlei Hover-Feedback: Der Spieler weiß vor dem Linksklick nicht, welche Truppe er treffen würde (`troopAt`-Schwelle 30 px, index.html:540, ist bei 12-px-Soldaten auf dem Schirm eng).
- **SPEC-Bezug:** "Auswahl hervorgehoben" (Z. 79).
- **Änderungsvorschlag:** (a) Auswahlring deutlicher: `lineWidth: 2.5`, Teamfarbe statt Weiß (z. B. helles Blau `#9fc2ff`), plus kleine rotierende Eckeck-Markierungen am Kreis; (b) Hover-Highlight: im `mousemove`-Handler (ohne Drag) `troopAt` aufrufen und die getroffene eigene Truppe mit schwachem Ring (alpha 0.4) vorzeichnen — ein `G.hover`-Feld genügt.

**W3 — HP-Abdunklung untergräbt die Blau/Rot-Farbsemantik**
- **Befund:** `drawSoldier` skaliert die Körperfarbe mit `hpFrac` (index.html:687–690): Bei 25 % LP wird Blau zu ~RGB(40,56,71) — ein dunkles Grau-Blau — und Rot zu ~RGB(74,39,39) — ein dunkles Grau-Rot. Der Beobachter sieht in der roten Masse "vereinzelt dunkle Einheiten", ohne sie einordnen zu können. Verwundete Truppen verlieren genau dann ihre Teamfarbe, wenn die Lage spannend wird.
- **SPEC-Bezug:** "Farben/Flaggen klar unterscheidbar (Spieler blau, KI rot)" (Z. 74–75).
- **Änderungsvorschlag:** Teamfarbe konstant halten; LP stattdessen anders codieren — z. B. Mini-HP-Balken (2 px) unter dem Soldaten erst ab <100 % HP, oder Sättigung statt Helligkeit reduzieren, oder kleiner werdender Innenkreis. Teamfarbe darf nie die Information "Zustand" tragen.

**W4 — Treffer-Feedback nur als kaum sichtbare Partikel; kein Schadens-/Counter-Bezug**
- **Befund:** Der Beobachter sieht "oben links kleine rote Partikel (Kampfspuren)" — im Code existiert aber **kein Partikelsystem**; was er sieht, sind vermutlich abgedunkelte (verwundete/tote) Soldaten am Bildrand. Es gibt keinerlei Treffer-Feedback: kein Aufblitzen beim Schlag, keine Schadenszahlen, kein Ansturm-Impuls der Kavallerie, kein Burst-Signal der Plänkler. Die Counter-Mechanik — laut SPEC "Kern des Spiels" (Z. 31) — ist für den Spieler unsichtbar.
- **Änderungsvorschlag:** Minimaler Satz: (a) Trefferblitz: getroffener Soldat 150 ms hell umranden (`s.hitFlash = G.simTime` in `applyDamage`, index.html:333, im `drawSoldier` abfragen); (b) Kavallerie-Ansturm mit Geschwindigkeits-Staubspur, wenn `speedSmooth > CHARGE_SPEED` (index.html:356); (c) optional kleine Schadenszahlen (float text) nur bei Counter-Treffern (mult > 1.5), um das Zählsystem erlebbar zu machen.

**W5 — Moral/Flucht auf dem Feld nicht lesbar**
- **Befund:** "FLUCHT!" erscheint ausschließlich in der Sidebar-Karte (index.html:1069–1071). Auf dem Feld rennt eine Truppe Richtung Kartenrand — ohne weiße Fahne, ohne Icon. Da Flucht zählt wie Tod (Siegbedingung, index.html:1028–1037) und der Spieler fliehende Truppen zurückrufen kann (index.html:588–590), ist das eine spielrelevante Information, die auf dem Feld fehlt.
- **SPEC-Bezug:** Moral-Mechanik Z. 51–53; Sidebar soll Moral zeigen (Z. 78) — tut sie, aber der Feldbezug fehlt.
- **Änderungsvorschlag:** In `drawTroop` bei `t.routing` ein weißes Fähnchen/Icon über dem Anker zeichnen und die Soldaten ggf. ent-sättigt darstellen. Ergänzend (aus shot 4): Der Ergebnis-Screen zeigt "Geflohene Truppen", die Sidebar danach "Bereit" mit vollen Balken — sicherstellen, dass dies der Neuaufstellungs-Zustand nach Restart ist und kein Reset-Bug (Verdacht prüfen: `init()` setzt `G.fled` korrekt zurück, index.html:1140 — vermutlich OK, aber der Beobachter-Kontext legt nahe, den Restart-Flow einmal manuell zu verifizieren).

---

### MINOR

**M1 — Hilfeleiste überläuft bei schmalen Fenstern** — `#hint` ist eine einzeilige, nicht umbrechende Leiste (index.html:79–83, 121–125); laut Beobachter "könnte auf schmalen Fenstern abgeschnitten sein". Fix: `flex-wrap`/`font-size: 11px` + `white-space: normal`, oder zweizeiliges Layout unter ~1000 px Viewport per Media-Query.

**M2 — Befehlsmarker farblich doppeldeutig** — Der Bewegungs-Marker ist hellgrün (`#a7e0a7`, index.html:766) auf grünem Gras, der Angriffs-Marker hellrot (`#ff9a9a`/`#ff5b5b`, index.html:771, 780) auf roten KI-Truppen. Grün ist zudem sonst unbelegt (Moral-Balken-Grün ≠ Befehl-Grün). Fix: Teamfarbe für eigene Befehle verwenden (blauer Move-Ring), Angriffsmarker gelb/orange (`#ffb347`) statt Rot — Rot bleibt exklusiv "Feind".

**M3 — Keine Kartenbegrenzung sichtbar** — Welt 2600×1700, aber das Terrain endet ohne jede Kante; außerhalb liegt `#141a10`-Schwarz (index.html:752). Bei Zoom 0.35 sieht man harte Terrain-Schnittkanten. Fix: dezenter Randstreifen (Zaun-/Baumlinie oder dunkleres Grasband) entlang der Weltgrenze in `buildTerrain` (index.html:641).

**M4 — Kleine, kontrastarme Statuslabels** — `.card .state` (10 px, `#a7b598`, index.html:64) und `.card .crow` (11 px) sind die kleinsten Texte der UI; der Beobachter merkt "'Auto: AN'/'Bereit'-Labels klein und kontrastarm" an. Fix: 11→12 px für `.state`, Kontrast `#c4d2b4`.

**M5 — Pause-Overlay hat keine Neustart-Option** — Das Pause-Panel (index.html:1124–1126) bietet nur "P oder ESC zum Fortsetzen"; ein Neustart erfordert Match-Ende oder Reload. Kleinigkeit, aber für ein 5–10-Minuten-Match praktisch: Button "Schlacht neu starten" auch im Pause-Panel.

**M6 — Terrain-Dekor ist frei verteilt, keine Schlachtfeld-Dramaturgie** — 46 Felsen/24 Bäume rein zufällig (index.html:654–669), teils mitten in den Aufstellungszonen. SPEC erlaubt Optionales (Z. 76–77), aber zufällige Felsen unter Formationen stören die Lesbarkeit minimal. Fix: Spawn-Frei-Haltezone um die Deploy-Punkte (Radius ~200 px) in `buildTerrain`.

---

## Zusammenfassung nach Review-Kriterien

| Kriterium | Bewertung | Kernaussage |
|---|---|---|
| Visuelle Hierarchie | ⚠️ | Rahmen-UI (Topbar/Sidebar/Overlay) klar; auf dem Feld fehlt die oberste Ebene (Truppen-Identität) — K1 |
| Lesbarkeit Einheiten/Formationen | ⚠️ | Waffen-Silhouetten & Teamfarben im Prinzip gut (SPEC-konform "Kreis + Waffe"), aber Formation zerfällt im Gefecht (K3), HP-Abdunklung verwässert Farben (W3) |
| UI-Konsistenz | ✅ gut | Karten, Topbar, Overlay, Hilfe konsistent gestaltet; M1/M4 sind Feinschliff |
| Farbsemantik (blau/rot) | ⚠️ | Grundsemantik sauber (TEAM_COLOR index.html:672, Badges index.html:75–76), aber W2/W3/M2 verwässern sie in der Praxis |
| Kampfbezug (Projektile/Marker/Feedback) | ❌ schwach | W1, W4, W5 — der spannendste Teil (Schüsse, Treffer, Counter, Flucht) ist auf dem Feld nahezu unsichtbar |
| Deutschsprachigkeit | ✅ | Vollständig deutsch; "Formation Battle" als Eigenname korrekt beibehalten (SPEC Z. 80); `lang="de"` gesetzt |
| SPEC-Abweichungen | ⚠️ | "Geometrie sichtbar!" nur in Ruhe erfüllt (K3); "Auswahl hervorgehoben" nur in Sidebar (W2); "Anti-Übersichtlichkeits-Fehler" durch K1/K2 verletzt; restliche SPEC (Header-Kommentar, 1 Datei, keine Deps, 60 FPS, fixer Timestep) erfüllt |

**Top-3-Maßnahmen (höchster Wirkung/Aufwand):** K2 (Startkamera, 1 Zeile) → K1 (Feld-Banner, ~10 Zeilen) → W1 (Projektile sichtbar machen, ~5 Zeilen).
