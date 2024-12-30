choirsupport
============

Hulpprogramma's voor het maken van oefenbestanden voor alle partijen van een koor.

## Installatie

1. Installeer [Python 3](https://www.python.org/downloads/).
2. Installeer choirsupport met `pip install choirsupport`.

Voor het bewerken van MIDI-bestanden gebruikt choirsupport de `mido` bibliotheek. Deze wordt automatic geïnstalleerd als
je choirsupport installeert. Om de MIDI-bestanden om te zetten naar mp3-bestanden heb je extra software nodig. Standaard
wordt verondersteld dat je [Fluidsynth] en [FFmpeg] gebruikt. Fluidsynth zet de MIDI-bestanden om naar WAV-bestanden en
ffmpeg zet de WAV-bestanden om naar mp3-bestanden. Beide programma's zijn gratis en open source.

[Fluidsynth]: https://www.fluidsynth.org/

[FFmpeg]: https://ffmpeg.org/

## Gebruik

Choirsupport helpt enkel bij het maken van oefenbestanden voor alle koorpartijen. Het gaat ervan uit dat er een master
MIDI-bestand is met alle partijen. Dit bestand kun je maken met een programma zoals [MuseScore]. Maak hierin de
partituur met alle partijen en exporteer deze naar een MIDI-bestand. Gebruik vervolgens het volgende commando om de
oefenbestanden te maken:

```shell
create-choir-parts master.mid output-dir
```

Dit maakt voor elke partij in het master-MIDI-bestand een apart MIDI-bestand met de naam `output-dir/master-part.mid`.
Op de plaats van `part` komt een label voor de partij, zoals `S1` voor de eerste sopraanpartij, `Bar` voor de baritons,
etc. Daarnaast wordt er een MIDI-bestand gemaakt met alle partijen, met de naam `output-dir/master-SATB.mid`. Dit is in
feite hetzelfde als het master-MIDI-bestand, maar dan met het volume van de partijen aangepast zoals geconfigureerd.

[MuseScore]: https://musescore.org/


