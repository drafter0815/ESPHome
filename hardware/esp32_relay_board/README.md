# ESP32 Touch Relay Controller – KiCad Startprojekt

Dieses Verzeichnis enthaelt ein hierarchisches KiCad-6/7-Projekt als Ausgangspunkt fuer die weitere Entwicklung einer Platine mit ESP32, 3" Touchdisplay, 16 Relais und 4 Servokanälen.

## Dateien

- `esp32_relay_board.kicad_pro` – Projektdatei zum Oeffnen in KiCad.
- `esp32_relay_board.kicad_sch` – Haupthierarchie mit Unterblaettern.
- `esp32_relay_board.kicad_pcb` – Visualisiertes Platzierungs-Layout (per KiCad-CLI generierbar) als Orientierung fuer das Leiterplattendesign.
- `power.kicad_sch` – Platzhalter fuer Netzteil- und Schutzbeschaltung.
- `mcu_display.kicad_sch` – Platzhalter fuer ESP32, Display und Touch.
- `relays.kicad_sch` – Platzhalter fuer Optokoppler- und Relaisstufe.
- `servo_i2c.kicad_sch` – Platzhalter fuer PCA9685 und Servoanschluesse.
- `scripts/generate_board.py` – Python-Skript, das den aktuellen PCB-Entwurf mithilfe der KiCad-Python-API erzeugt.

## Weiteres Vorgehen

1. Falls du das platzierte Layout frisch erzeugen moechtest, fuehre in diesem Ordner `python3 scripts/generate_board.py` aus. Das Skript nutzt KiCad (`pcbnew`) und laesst sich ohne GUI ueber den KiCad-CLI-freundlichen Python-Interpreter starten.
2. Oeffne danach `esp32_relay_board.kicad_pro` in KiCad 6 oder neuer.
3. Folge den Hinweisen in `NOTES.md`, um Bauteile, Netznamen und Schutzbeschaltungen gezielt zu platzieren.
4. Definiere die genauen Netzbezeichnungen und Steckverbinder entsprechend deiner Mechanik.
5. Erstelle anschliessend ein neues PCB und synchronisiere das Netz aus dem Schaltplan.

> Hinweis: In dieser Umgebung laesst sich KiCad selbst nicht ausfuehren. Das bereitgestellte Projekt dient daher als sauber strukturierter Startpunkt, den du lokal in KiCad oder Altium weiterverarbeiten kannst.

## KiCad-Bibliotheken beziehen

Falls dir lokal die offiziellen KiCad-Bibliotheken fehlen, findest du im Unterordner `scripts/` das Skript `clone_kicad_libs.sh`. Fuehre es in einem leeren Verzeichnis mit Internetzugang aus, um alle offiziellen Symbol- und Footprint-Repositorys von GitHub zu klonen und auf den neuesten Stand zu bringen.
