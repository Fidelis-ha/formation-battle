# Screenshot-Beschreibungen zur Symbol-Änderung (Kairos, neutral)

Dateien: .reviews/shots/7-sidebar-icons.png, 8-feld-symbole.png,
10-detail-kavallerie.png, 11-detail-speere.png

## 7-sidebar-icons.png
Desktop-Ansicht, Sidebar-Karten auf 1,6-facher Größe skaliert.
Alle 5 Icons jetzt GEFÜLLTE Silhouetten in Hellblau (currentColor):
1 Speer (diagonal, Spitze), 2 Axt (Stiel + halbmondförmiges Blatt),
3 Schwert (Parierstange erkennbar), 4 Bogen (Kurve + Sehne + Pfeil),
5 Pferdekopf. Beobachtung (Kairos): Bogen/Pferd/Axt eindeutig;
Speer vs. Schwert ähneln sich im Kern (beide lange dünne Diagonale),
Unterschied (Spitze vs. Parierstange) bei ~30px schwer erkennbar.

## 8-feld-symbole.png
Spielzoom 1.3, aktives Gefecht. Feld-Soldaten: Kreise in Teamfarbe
mit dunkler Kontur; Waffen-Silhouetten vorhanden, aber bei diesem
Zoom klein. Bildanalyse lasse keine Typunterscheidung erkennen
(Kreis-mit-Strich-Impression), Pixelprobe beweist aber gerenderte
dunkle Silhouetten (736 dunkle Pixel im 60×60-Fenster um einen
Kavallerie-Soldaten bei Zoom 3).

## 10-detail-kavallerie.png / 11-detail-speere.png
Zoom 2.2–3.0 Detailansichten. Kavallerie: größer als Standard
(radius 9 vs 6), Pferdekörper/Hals-Kontur + Reiter-Punkt im Code
vorhanden und gerendert (Pixelprobe). Waffen: dunkle Silhouetten
(#1c2016, lineWidth 2.4) + gefüllte Zusatzformen (Axtblatt,
Schild-Punkt, Pfeil).

## Leitfrage des Reviews
"Sind die 7 Einheiten bei SPIEL-Zoom (0.7–1.3) auf dem Feld und in
der Sidebar auf einen Blick unterscheidbar?" Bewerte insbesondere:
- Feld-Silhouetten bei Spielzoom: reicht die Detailtiefe oder
  verschwimmen die Unterschiede (insbesondere infantry vs
  swordsman, spearman vs skirmisher)?
- Kavallerie-Größenvorteil bei Spielzoom wahrnehmbar (+3px)?
- Sidebar: Speer vs. Schwert bei Standardgröße unterscheidbar?
- Vorschläge erwartet: konkret (z.B. lineWidth erhöhen, Radius
  stärker differenzieren, Formvereinfachung für kleine Zoomstufen,
  ggf. LOD: ab zoom < 0.8 stärker vereinfachte, typische Umrisse).
