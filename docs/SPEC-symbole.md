# SPEC-Addendum — Einheitensymbole (Erkennbarkeit)

Erweitert die bestehende SPEC. Keine Mechanik-/Balance-Änderungen.

## Ziel
Jede der 7 Einheiten ist auf einen Blick unterscheidbar — im Sidebar-UI
(klein, ~20px) und auf dem Schlachtfeld (kleine Figuren, Top-Down).

## Sidebar-Icons (Inline-SVG, gefüllt, kein Strichmännchen)
| Typ | Emblem |
|---|---|
| spearman | Rundschild mit aufgesetztem Speer (Schild kreisförmig gefüllt, Speer diagonal) |
| housecarl | Streitaxt (Kopf + Stiel, klare Axtsilhouette) |
| infantry | gerades Langschwert mit Parierstange |
| archer | Bogen mit Sehne + Pfeil quer |
| skirmisher | Wurfspeer kurz + Handschlaufe angedeutet |
| cavalry | Pferdekopf-Silhouette (klar erkennbar, nicht abstrakt) |
| swordsman | geschwungener Kriegsschwert-Silhouette (unterscheidbar von infantry: kürzer/breiter Klingenwinkel) |
- Icons in `currentColor`, damit die Karten-Farbgebung greift.
- Als gefüllte Pfade (fill), nicht nur stroke — Lesbarkeit bei 16-24px.
- Formen müssen sich bei kleiner Größe deutlich unterscheiden (Kontrastprüfung
  im Review per Screenshot).

## Feld-Darstellung (Canvas, drawSoldier)
- Jeder Typ behält Kreis-Körper in Teamfarbe, ABER die Waffen-Silhouette wird
  deutlicher und typspezifisch:
  - spearman: langer Speer + kleiner Rundschild-Punkt
  - archer: Bogen-Kurve mit Sehne, erkennbar gebogen
  - skirmisher: kurzer Wurfspeer, dargestellt zum Wurf angesetzter Arm
  - infantry: gerades Schwert
  - swordsman: breiteres/gebogtes Schwert, erkennbar anders als infantry
  - housecarl: Axt (Stiel + halbmondförmiger Kopf)
  - cavalry: TRUPPE GRÖSSER ZEICHNEN (radius +3) UND Reiter-Pferdekontur:
    länglicher Körper + Kopf vorn (Pferdesilhouette), Reiter-Punkt oben —
    auf einen Blick als „beritten" lesbar
- Teamfarbe konstant (blau/rot), Silhouetten dunkel abgesetzt (Kontrast).
- Mini-HP-Balken & Banner unangetastet lassen (Positionen dürfen bleiben).

## Out of Scope
- Keine Animationen, keine Asset-Dateien, keine externen Icon-Bibliotheken,
  keine Balance-Änderungen.
