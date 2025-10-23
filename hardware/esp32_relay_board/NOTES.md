# Arbeitsnotizen zum ESP32-Relay-Board

Diese Notizen fassen die Zielsetzung des Projekts zusammen und ordnen die Signale den Hierarchieblaettern des KiCad-Projekts zu.
Sämtliche Schaltpläne liegen inzwischen als KiCad-7-S-Expression vor; das Skript `scripts/convert_legacy_sch.py` dokumentiert die Konvertierung aus dem alten V4-Format.
Die Hinweise dienen als Referenz, wenn du den Schaltplan in KiCad weiter ausarbeitest oder zusaetzliche Tools (z. B. Altium) verwendest.

## Signaluebersicht

| Bereich         | Signal               | Beschreibung |
|-----------------|----------------------|--------------|
| Netzversorgung  | AC_L / AC_N / PE     | 230-V-Zuleitung, Schutzleiter. |
| Netzteil        | V12                  | 12-V-Schiene fuer Relais und Servoversorgung. |
|                 | V5                   | 5-V-Schiene fuer ESP32, Display und Touch. |
|                 | V3V3                 | 3,3-V-Logikversorgung. |
| Relaisansteuerung | GPIO_RELAY0 .. GPIO_RELAY15 | Ansteuerleitungen (vom ESP32 ueber Optokoppler). |
|                 | NO1 .. NO16 / NC1 .. NC16 | Arbeitskontakte (Schliesserkontakt). |
|                 | LOAD_COM0 .. LOAD_COM3 | Sammelschienen fuer vier Vierergruppen. |
| Servo-Ausgaenge | PWM_SERVO0 .. PWM_SERVO3 | PWM-Signale vom PCA9685. |
|                 | V5_SERVO            | 5-V-Bus fuer Servos. |
| Touchdisplay    | SPI_MOSI, SPI_MISO, SPI_SCLK, TFT_CS, TFT_DC | SPI-Anschluesse fuer das TFT. |
|                 | TOUCH_CS, TOUCH_IRQ  | Touch-Controller (XPT2046 o. ae.). |
|                 | LCD_RST, LCD_BL      | Reset und Hintergrundbeleuchtung. |
| Kommunikation   | I2C_SCL, I2C_SDA     | I2C-Bus fuer PCA9685 und Erweiterungen. |
| Debug           | UART_TX, UART_RX     | Programmierschnittstelle des ESP32. |

## Referenz der Stiftsockelleisten

| Bezeichner | Pins | Zweck | Signalzuordnung |
|------------|------|-------|-----------------|
| J1         | 21   | ESP32-Steuerheader | GND, V5, V12, I2C (SCL/SDA) sowie GPIO_RELAY0..GPIO_RELAY15 als Ansteuerleitungen. |
| J2         | 21   | Relais-Treiber-Header | Gleiche Pinbelegung wie J1 zur Anbindung der Optokoppler- und Treiberstufe. |
| J3         | 16   | Last-/Klemmen-Header | LOAD_COM0..LOAD_COM3 sowie die jeweiligen NO/NC-Kontakte der Relais. |

## Empfohlene Arbeitsschritte in KiCad

1. **Hierarchie oeffnen** – Starte mit `esp32_relay_board.kicad_pro` und oeffne die Untersheets ueber Doppelklick.
2. **Schutzbeschaltung einfuegen** – Im Blatt `power.kicad_sch` platziere Sicherung, Varistor, NTC und das IRM-20-12 Modul. Richte V12/V5/V3V3 als globale Netze ein.
3. **ESP32 & Display verdrahten** – Im Blatt `mcu_display.kicad_sch` verwende ein ESP32-WROOM-32 Symbol aus der KiCad-Bibliothek, fuege 3"-TFT (z. B. ILI9341) als Steckverbinder hinzu und beschrifte die Leitungen entsprechend der Tabelle oben.
4. **Relaismatrix modellieren** – Lege im Blatt `relays.kicad_sch` eine vierfache Struktur aus Optokoppler (PC817), Treibertransistor (S8050), Relaisspule (SRD-12VDC-SL-C) und Schraubklemme an. Kopiere die Struktur 16-fach und verbinde die Steuerleitungen mit `GPIO_RELAY*` und verknuepfe die Ausgaenge mit `DRV*` zu den Relais-Spulen.
5. **Servo-I2C erweitern** – Platziere den PCA9685 im Blatt `servo_i2c.kicad_sch`, fuege 4x3-polige Servo-Stiftleisten hinzu und verbinde sie mit `PWM_SERVO*`, `V5_SERVO` und GND. Plane einen grossen Elko (>=470 µF) fuer Servos.
6. **Netznamen & Off-Sheet-Labels** – Verwende die in diesem Dokument genannten Signale, damit die Verbindung zwischen den Blaettern eindeutig ist.
7. **Design Rules** – Lege in KiCad passende Netzklassen fest (z. B. "Mains", "Power", "Logic") mit den jeweils benoetigten Leiterbahnbreiten und Clearance.
8. **Sync zum PCB** – Wenn der Schaltplan fertig ist, aktualisiere das PCB (`Tools -> Update PCB from Schematic`) und beginne mit dem Routing.

> Tipp: Solltest du die offiziellen KiCad-Symbole und -Footprints noch nicht lokal haben, kannst du das Skript `scripts/clone_kicad_libs.sh` verwenden, um sie aus den GitHub-Repositorys der KiCad-Organisation zu beziehen.

## Export nach Altium

Fuer einen Wechsel zu Altium kannst du das KiCad-Projekt in KiCad 7 als `EDIF` exportieren (`Datei -> Exportieren -> Netliste -> EDIF`). Diese Netliste laesst sich in Altium Designer importieren und dort weiterbearbeiten.

## Dateien fuer schnelle Navigation

- `power.kicad_sch`: Netzteil, Sicherungen, Schutz.
- `mcu_display.kicad_sch`: ESP32, Touchdisplay, I2C-Bus.
- `relays.kicad_sch`: 16-fach Relaistreiber.
- `servo_i2c.kicad_sch`: PCA9685, Servoausgaenge und Versorgung.
- `esp32_relay_board.kicad_pcb`: Geroutetes Konzeptlayout mit drei Stiftsockelleisten (J1/J2/J3) und horizontal gefuehrten Sammelschienen fuer alle 16 Relais. Die Datei wird von `scripts/generate_board.py` erzeugt und laesst sich jederzeit neu schreiben.
- `esp32_relay_board_detail.txt`: ASCII-Plan des Layouts fuer Umgebungen ohne Binaer-Support, generiert durch `scripts/generate_ascii.py`.

Diese Notizen sollen verhindern, dass Details aus dem vorherigen Chat verloren gehen, und erleichtern dir den direkten Einstieg in das KiCad-Projekt.
