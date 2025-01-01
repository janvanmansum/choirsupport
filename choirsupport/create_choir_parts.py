import argparse
import logging
import os.path

from choirsupport.common import init, recursive_merge
from choirsupport.copy_midi import copy_midi, find_track_by_name
import yaml
from mido import MidiFile

from choirsupport.instruments import MIDI_INSTRUMENTS


def log():
    return logging.getLogger(__name__)


def load_settings(input_file):
    # Look for a Yaml file with the same base name as the input MIDI file
    settings_file = os.path.splitext(input_file)[0] + '.yml'
    if not os.path.exists(settings_file):
        return {}
    # Load the settings from the Yaml file
    with open(settings_file) as f:
        settings = yaml.safe_load(f)
    return settings


def export_part(input_midi, output_file, part, instruments, volumes, volume_for_part=None, part_piano_volume=None):
    log().info("Exporting part %s to %s", part, output_file)
    log().debug("START export_part for part %s", part)
    if part_piano_volume is not None:
        piano_for_part_track = {
            'name': 'Piano for part',
            'instrument': 0,
            'volume': part_piano_volume,
            'melody_from': part
        }
    else:
        piano_for_part_track = None
    if volume_for_part is not None:
        volumes[part] = volume_for_part

    log().debug("Exporting part %s to %s with the following settings:", part, output_file)
    log().debug("Instruments: %s", instruments)
    log().debug("Volumes: %s", volumes)
    log().debug("Piano for part track: %s", piano_for_part_track)

    midi_copy = copy_midi(input_midi, instruments, volumes, piano_for_part_track)
    midi_copy.save(output_file)
    log().debug("END export_part for part %s", part)
    log().debug("---------------------------------")


def get_output_file_name(input_midi, output_dir, part):
    base_name = os.path.splitext(os.path.basename(input_midi))[0]
    return os.path.join(output_dir, f"{base_name}-{part}.mid")


def get_default_volume_for_part(part, settings):
    default_override = settings['volumes'].get('default_override', {})
    return default_override.get(part, settings['volumes']['default'])


def main():
    config = init()
    parser = argparse.ArgumentParser(description="Export choir parts with customized volumes and instruments",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input_midi", help="Input MIDI file")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("parts", help="Specific parts to process (default: process all parts)", nargs='*')
    args = parser.parse_args()

    output_dir = os.path.expanduser(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    settings = recursive_merge(config, load_settings(args.input_midi))

    women = settings['women_voices']
    men = settings['men_voices']
    voices = {**women, **men}
    instruments = {}

    for v in women:
        instruments[v] = MIDI_INSTRUMENTS[settings['women_instrument']]

    for v in men:
        instruments[v] = MIDI_INSTRUMENTS[settings['men_instrument']]

    volumes = {}

    for v in voices.keys():
        volumes[v] = get_default_volume_for_part(v, settings)

    # Set default volumes for special tracks
    volumes['Piano'] = settings['volumes']['piano']
    # Work-around for problem in MuseScore (not possible to rename tracks)
    volumes['Piano 2'] = settings['volumes']['piano']
    volumes['Wood Blocks'] = settings['volumes']['wood_blocks']

    input_midi = os.path.expanduser(args.input_midi)
    midi = MidiFile(input_midi)

    voices_to_process = args.parts if args.parts else voices.keys()

    for v in voices_to_process:
        if find_track_by_name(midi, v):
            output_file = get_output_file_name(input_midi, output_dir, voices[v])
            export_part(midi, output_file, v, instruments.copy(), volumes.copy(), settings['volumes']['part'],
                        settings['volumes']['part_piano'])
        else:
            log().warning(f"Skipping part {v} because it was not found in the input MIDI file")
    # Make an export for SATB
    if len(voices_to_process) > 1:
        for v in voices_to_process:
            volumes[v] = settings['volumes']['satb']
        output_file = get_output_file_name(input_midi, output_dir,
                                           create_label_for_voices_combination(voices_to_process))
        export_part(midi, output_file, 'SATB', instruments, volumes)


def create_label_for_voices_combination(voices):
    label = ""
    if "Soprano" in voices or "Mezzo-soprano" in voices:
        label += "S"
    if "Alto" in voices or "Alto 1" in voices or "Alto 2" in voices:
        label += "A"
    if "Tenor" in voices or "Tenor 1" in voices or "Tenor 2" in voices:
        label += "T"
    if "Baritone" in voices or "Bass" in voices:
        label += "B"
    return label


if __name__ == "__main__":
    main()
