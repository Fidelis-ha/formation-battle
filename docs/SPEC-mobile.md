# SPEC-Addendum — Mobile Steuerung (Touch)

Erweitert docs/SPEC-formation-battle.md. Alle Bestandsmechaniken unverändert.

## Ziel
Formation Battle ist auf Smartphones (Touch, portrait UND landscape) voll
spielbar; Desktop-Steuerung bleibt parallel vollständig erhalten.

## Touch-Interaktion (Canvas)
- Implementierung über Pointer Events (pointerdown/move/up/cancel), nicht
  über separaten Touch-Handler-Duplikat; Maus-Logik bleibt wirksam.
- `touch-action: none` auf dem Canvas; kein Text-Auswahl/Zoom-Dialog.
- Ein Finger:
  - Kurzer Tap (Bewegung < ~12 px, Dauer egal) auf EIGENE Truppe → auswählen.
  - Kurzer Tap auf FEIND-Truppe (mit ausgewählter eigener) → Angriffsbefehl.
  - Kurzer Tap auf freien Boden (mit ausgewählter eigener) → Marschbefehl.
  - Tap ohne Auswahl auf Feind → nichts (kein versehentlicher Befehl).
  - Ziehen ab Schwellwert (> 12 px) → Kamera-Pan (ein Finger).
- Zwei Finger: Pinch = Zoom um den Mittelpunkt der Finger (Klemmen an
  bestehende Zoom-Grenzen); Fingerabstand-Änderung > Pan-Verschiebung.
- Doppeltipp-Zoom ist NICHT belegt (keine Konflikte).
- Mindest-Touch-Zielgröße: Auswahlsuche tropeAt mit größerem Radius bei
  Pointer-Typ touch (z. B. 30 px Weltdistanz statt 30 screen px anpassen —
  so wählen, dass 44-px-Finger-Äquivalent erreicht wird).

## Responsive UI
- `<meta name="viewport" content="width=device-width, initial-scale=1,
  maximum-scale=1, user-scalable=no, viewport-fit=cover">` ergänzen.
- Media Query (max-width: 820px ODER coarse pointer):
  - Sidebar kollabiert: 5 Truppenkarten als horizontale Leiste UNTEN,
    kompakt (Icon + Nummer + Soldatenzahl + Statusfarbe), tappbar, ≥44 px hoch.
  - Topbar bleibt oben (kompakter), Hilfezeile zeigt TOUCH-Text:
    „Tippen: wählen · Tippen auf Feind: Angriff · Ziehen: Kamera · Pinch: Zoom".
- Desktop-Layout (Sidebar links, Maus-Hinweise) unverändert.
- Canvas füllt viewport, devicePixelRatio-Cap 2 (Performance).

## Simulation
- Unverändert (keine Balance-Änderungen, kein schwierigerer/einfacherer Modus).

## Qualität
- Keine doppelten Befehle (tap-to-select darf nicht gleichzeitig pan auslösen
  und umgekehrt); Punkt-Erkennung mit Bewegungs-Schwelle.
- contextmenu-Unterdrückung auch für Long-Press-Touch.
- Getestet: Touch-Emulation im Browser (CDP), Portrait 390×844 und Landscape
  844×390, sowie Desktop-Regression (Maus unverändert).
