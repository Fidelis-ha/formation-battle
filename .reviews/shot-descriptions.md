# Screenshot-Beschreibungen (Kairos, neutral-observierend, für Design-Review)

Alle Screenshots: 1280x578 Viewport, dunkelgrünes Gras-Terrain, HTML5-Canvas-Spiel.
Dateien: .reviews/shots/1-start.png, 2-gefecht.png, 3-spaet.png, 4-ende.png

## 1-start.png
Startaufstellung, 00:00 Uhr-Anzeige. Keine Einheiten im sichtbaren Bereich
(Kamera zentriert auf Kartenmitte, Armeen links/rechts außerhalb der Ansicht
bei Zoom 0.72). Linke Sidebar: 5 Truppenkarten (Speerkämpfer 12/12, Hauscarls
10/10, Infanterie 12/12, Bogenschützen 12/12, Kavallerie 10/10), jeweils
Icon, grüner Balken, Status "Bereit", Auto: AN. Karte 1 hellblau umrandet
(ausgewählt). Oben: blaues "Spieler"-Badge, Uhr, rotes "Gegner"-Badge. Unten:
Steuerungshilfe (Linksklick/Rechtsklick/Mausrad/Mittelklick/Q/1-5/P-ESC).

## 2-gefecht.png
Aktives Gefecht, Uhr 00:05. Zwei rot/rosa Formationen sichtbar: eine große
(20+ Einheiten) Mitte-links in diagonaler/keilförmiger Ordnung, eine kleinere
unten links (15-20) in Keilform. Vereinzelt dunkle Einheiten in der roten
Masse. Blaue Einheiten NICHT klar erkennbar (off-screen oder verdeckt).
Sidebar: Karte 1 "Speerkämpfer 8/12, FLUCHT!" mit rotem Balken (rot),
Karte 2 "Hauscarls 9/10, Gefecht", Karte 3 "Infanterie 12/12, Gefecht",
Karten 4-5 "Bereit". Oben links kleine rote Partikel (Kampfspuren).
KEINE Projektile erkennbar. KEINE Auswahl-/Truppen-Marker auf dem Feld
sichtbar. Formationen wirken als lockere Keile, nicht als klare Reihen.

## 3-spaet.png
Späte Schlachtphase. (Nicht separat von mir analysiert — gleiche
Darstellungsprinzipien wie 2-gefecht.png zu erwarten.)

## 4-ende.png
Sieg-Overlay über abgedunkeltem Schlachtfeld. Zentrales dunkles Panel mit
hellgrünem Rahmen: Titel "SIEG" (leuchtend grün, Serifenlos, Letterspacing),
Statistiktabelle (Schlachtdauer 12:33, Verluste Spieler 23 Soldaten, Verluste
Gegner 41 Soldaten, Geflohene Truppen Spieler 1, Gegner 2 — Labels links,
fette Werte rechts), blauer Button "Neue Schlacht". Rand-UI (Topbar, Sidebar,
Hilfe) durch Overlay abgedunkelt, aber lesbar. Truppenkarten zeigen alle
"Bereit", volle grüne Balken (Neuaufstellung nach Neustart sichtbar).

## Von Kairos vorgemerkte Beobachtungen (zur Prüfung, nicht bewertend)
- Kein sichtbarer Auswahl-Ring/Marker um die gewählte Truppe auf dem Feld.
- Keine Truppen-Nummern (1-5) oder Banner auf dem Feld → Zuordnung
  Feldformation zu Sidebar-Karte unklar.
- Projektile (Pfeile/Speere) im Gefecht nicht erkennbar (evtl. zu klein,
  falscher Kamerabereich, oder Rendering-Problem).
- Treffer-Feedback auf dem Feld minimal (nur rote Partikel).
- Einheiten klein, Spielfeld wirkt leer bei Zoom 0.72; Startkamera zeigt
  KEINE der beiden Armeen.
- "Auto: AN"/"Bereit"-Labels klein und kontrastarm.
- Hilfeleiste unten einzeilig, könnte auf schmalen Fenstern abgeschnitten sein.
