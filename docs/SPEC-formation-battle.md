# SPEC — Formation Battle (Web-Rewrite)

Eigenständige Implementierung der Spielmechanik des itch.io-Prototyps
„Formation Battle" (Oki Aki). Kein Original-Code, keine Original-Assets —
nur die dokumentierten Spielmechaniken werden nachgebaut.

## Ziel
Ein einzelnes, selbstlaufendes HTML-Spiel: mittelalterliche Echtzeit-
Formationsschlacht, 5 Spieler-Truppen gegen 5 KI-Truppen, ein Match
in ca. 5–10 Minuten.

## Deliverable
- `index.html` — EINE Datei, alles inline (CSS, JS, Grafik per Canvas gezeichnet).
- Keine Build-Tools, keine externen Abhängigkeiten, kein Server nötig
  (funktioniert über file:// und jeden statischen Host).
- Läuft in aktueller Chrome/Firefox/Safari, Desktop (Maus + Tastatur).

## Spielmechanik

### Einheiten (7 Typen, jeweils 1 Truppe = Formation aus N Soldaten)
| Typ | Rolle | Stärken | Schwächen |
|---|---|---|---|
| Archer | Fernkampf (Bogen) | hoher konstanter Schaden auf Distanz | bricht im Nahkampf zusammen |
| Skirmisher | Fernkampf (Wurfspeer) | hoher Burst-Schaden, schnell | sehr fragil, kurze Reichweite |
| Infantry | Nahkampf | wendig, gut zum Flanken/Verfolgen | mittlere Werte überall |
| Housecarl | Nahkampf-Tank | schwer gepanzert, hält die Linie | langsam |
| Spearman | Abwehr | blockt Kavallerie-Anstürme, große Schilde | wenig Offensivschaden |
| Swordsman | Nahkampf-Sturm | hoher Angriff, bricht Formationen | kein Schild, anfällig gegen Fernkampf |
| Cavalry | Schocktruppe | schnell, verheerende Anstürme, Flanken | ANFÄLLIG GEGEN SPEERE (Multiplier!) |

### Counter-Multiplikatoren (Kern des Spiels, hardcoden)
- Spearman → Cavalry: x3.0 (Ansturm prallt ab)
- Cavalry → Archer/Skirmisher: x2.5 (Reiter metzeln Schützen)
- Archer/Skirmisher → Swordsman: x1.5 (unprotected assault)
- Swordsman → Archer/Skirmisher/Spearman: x2.0 (Nahkampf-Überlegenheit)
- Housecarl → alles Nahkampf: leichter Schadensbonus durch Rüstung (x1.3)
- Skirmisher-Burst: erste 3 Würfe x1.5, danach normal
- Algemeine Formel: dmg = base * counterMult * formationPenalty, mit
  leichtem Zufall (±15%). Keine Crit-Mechanik darüber hinaus.

### Formationen & Kampf
- Truppe = Formation aus 8–12 Einzelsoldaten in Reihen (Geometrie sichtbar!).
- Formation löst sich NICHT in Einzel-Mikro auf: Spieler befehligt die
  Truppe als Ganzes (Move-Befehl, Angriffsziel, Auto-Attack-Toggle).
- Formationsschaden: Truppe im Rücken/bei Flankenangriff erhält
  x1.5 Schaden (directional check relativ zur Ausrichtung).
- Nahkampf: Formationen aneinander = Soldaten kämpfen positionsgenau,
  vorderste Reihe zuerst.
- Ansturm (Cavalry): Bonus nur bei Bewegungsgeschwindigkeit > X beim
  Aufprall; Stehenbleiben = normaler Kampf.
- Moral (einfach): Truppe flieht/bricht, wenn >50% Verluste ODER
  Flankenangriff während Nahkampf; Fliehen = Rückzug Richtung Kartenrand,
  kann wieder gefasst werden (Spieler kann Truppe zurückrufen).

### Steuerung (wie der Prototyp)
- Linksklick: Truppe auswählen
- Rechtsklick: Bewegungsbefehl / Angriffsbefehl (auf Feindtruppe)
- Mausrad: Zoom, Mittelklick+Drag: Kamera
- Q: Auto-Attack-Modus der gewählten Truppe togglen
- 1–5: Truppen-Schnellauswahl
- ESC/P: Pause

### KI (5 Feindtruppen)
- Einfaches, aber sauberes Verhalten: Front-Truppen rücken vor, Fernkampf
  hält Distanz, Cavalry sucht Flanken, Speere bleiben gegen Kavallerie
  nahe der eigenen Linie. Keine Cheats: KI kennt dieselben Regeln,
  gleiche Sicht, gleiche Schadensformel.

### Sieg/Niederlage
- Matchende, wenn alle Truppen einer Seite tot ODER geflohen sind.
- Ergebnis-Screen mit Schlachtdauer und Verlusten je Seite.

### Darstellung
- Canvas 2D, Top-Down. Farben/Flaggen klar unterscheidbar (Spieler blau,
  KI rot). Einzelsoldaten als einfache, lesbare Figuren (Kreis + Waffen-Silhouette
  reicht), Terrain-Feld mit leichten Texturvarianten (Gras/Flecken, evtl. 1-2
  Hügel/Objekte als Sicht-/Deckungs-Andeutung — optional, nicht verpflichtend).
- UI: linke Leiste mit 5 Truppen-Karten (Typ-Icon, Soldatenzahl, Moral),
  Auswahl hervorgehoben; oben Match-Zeit; Anti-Übersichtlichkeits-Fehler vermeiden.
- Deutschsprachige UI-Texte (Spielname „Formation Battle" bleibt).

### Qualität
- 60 FPS-Ziel, requestAnimationFrame, fixer Timestep-Simulation.
- Responsives Canvas (Fullscreen, skaliert).
- Kein Speicherleck (Objekte entfernen, keine wachsenden Arrays).
- Kommentar-Kopf in index.html: MIT-Lizenz-Hinweis, Autor „Kairos für Marc",
  Hinweis auf die Inspirationsquelle (itch.io/okiaki/formation-battle) und
  dass es eine eigenständige Implementierung ist.

## Out of Scope (explizit)
- Kein Multiplayer/Hotseat, keine Kampagne, keine Einheiten-Progression,
  keine SFX/Musik (erst später, wenn gewünscht), keine Truppenauswahl vor
  dem Match (fixe Standard-Aufstellung beider Seiten).
