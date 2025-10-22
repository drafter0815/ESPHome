# ESP32 Touch Relay Controller – KiCad Startprojekt

Dieses Verzeichnis enthaelt ein hierarchisches KiCad-6/7-Projekt als Ausgangspunkt fuer die weitere Entwicklung einer Platine mit ESP32, 3" Touchdisplay, 16 Relais und 4 Servokanälen.

## Dateien

- `esp32_relay_board.kicad_pro` – Projektdatei zum Oeffnen in KiCad.
- `esp32_relay_board.kicad_sch` – Haupthierarchie mit Unterblaettern.
- `esp32_relay_board.kicad_pcb` – Geroutetes Referenz-Layout mit 3 Stiftsockelleisten (Steuerung, Treiber, Last) und exemplarischen Busführungen.
- `esp32_relay_board_detail.txt` – Reines Text-Blueprint in ASCII, erzeugt durch `scripts/generate_ascii.py`, funktioniert auch, wenn keinerlei Binärdateien übertragen werden dürfen.
- `power.kicad_sch` – Platzhalter fuer Netzteil- und Schutzbeschaltung.
- `mcu_display.kicad_sch` – Platzhalter fuer ESP32, Display und Touch.
- `relays.kicad_sch` – Platzhalter fuer Optokoppler- und Relaisstufe.
- `servo_i2c.kicad_sch` – Platzhalter fuer PCA9685 und Servoanschluesse.
- `scripts/generate_board.py` – Reines Python-Skript (ohne KiCad-Abhängigkeiten), das die KiCad-PCB-Datei inklusive Steckverbindern und Leiterbahnen neu generiert.

## Weiteres Vorgehen

1. Falls du das Referenzlayout frisch erzeugen moechtest, fuehre in diesem Ordner `python3 scripts/generate_board.py` aus. Das Skript schreibt die komplette `.kicad_pcb`-Datei neu und benoetigt keine KiCad-Installation.
2. Fuer eine schnelle textuelle Vorschau kannst du optional `python3 scripts/generate_ascii.py` ausführen; dabei entsteht bzw. aktualisiert sich `esp32_relay_board_detail.txt`.
3. Oeffne danach `esp32_relay_board.kicad_pro` in KiCad 6 oder neuer.
4. Folge den Hinweisen in `NOTES.md`, um Bauteile, Netznamen und Schutzbeschaltungen gezielt zu platzieren.
5. Definiere die genauen Netzbezeichnungen und Steckverbinder entsprechend deiner Mechanik.
6. Erstelle anschliessend ein neues PCB und synchronisiere das Netz aus dem Schaltplan.

> Hinweis: In dieser Umgebung laesst sich KiCad selbst nicht ausfuehren. Das bereitgestellte Projekt dient daher als sauber strukturierter Startpunkt, den du lokal in KiCad oder Altium weiterverarbeiten kannst.

## KiCad-Bibliotheken beziehen

Falls dir lokal die offiziellen KiCad-Bibliotheken fehlen, findest du im Unterordner `scripts/` das Skript `clone_kicad_libs.sh`. Fuehre es in einem leeren Verzeichnis mit Internetzugang aus, um alle offiziellen Symbol- und Footprint-Repositorys von GitHub zu klonen und auf den neuesten Stand zu bringen.
