# ESP32 Touch Relay Controller – KiCad Startprojekt

Dieses Verzeichnis enthaelt ein hierarchisches KiCad-6/7-Projekt als Ausgangspunkt fuer die weitere Entwicklung einer Platine mit ESP32, 3" Touchdisplay, 16 Relais und 4 Servokanälen.

## Dateien

- `esp32_relay_board.kicad_pro` – Projektdatei zum Oeffnen in KiCad.
- `esp32_relay_board.kicad_sch` – Haupthierarchie mit Unterblaettern.
- `power.kicad_sch` – Platzhalter fuer Netzteil- und Schutzbeschaltung.
- `mcu_display.kicad_sch` – Platzhalter fuer ESP32, Display und Touch.
- `relays.kicad_sch` – Platzhalter fuer Optokoppler- und Relaisstufe.
- `servo_i2c.kicad_sch` – Platzhalter fuer PCA9685 und Servoanschluesse.

## Weiteres Vorgehen

1. Oeffne `esp32_relay_board.kicad_pro` in KiCad 6 oder neuer.
2. Fuege in den Unterblaettern die tatsaechlichen Bauteile aus den Bibliotheken hinzu.
3. Definiere die genauen Netzbezeichnungen und Steckverbinder entsprechend deiner Mechanik.
4. Erstelle anschliessend ein neues PCB und synchronisiere das Netz aus dem Schaltplan.

> Hinweis: Dieses Projekt enthaelt bewusst nur strukturierende Platzhalter, damit du schnell auf Basis der vorgegebenen Architektur weiterarbeiten kannst.
