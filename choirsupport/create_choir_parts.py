import argparse
import logging
import os.path

from choirsupport.common import init
from choirsupport.copy_midi import copy_midi2, find_track_by_name
import yaml
from mido import MidiFile

from choirsupport.instruments import MIDI_INSTRUMENTS


def load_settings(input_file):
    # Look for a Yaml file with the same base name as the input MIDI file
    settings_file = os.path.splitext(input_file)[0] + '.yml'
    if not os.path.exists(settings_file):
        return None, None
    # Load the settings from the Yaml file
    with open(settings_file) as f:
        settings = yaml.safe_load(f)
    return settings


def export_part(input_midi, output_file, part, instruments, volumes, volume_for_part=None, part_piano_volume=None):
    print("START export_part for part", part)
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

    print("Exporting part", part, "to", output_file, "with the following settings:")
    print("Instruments:", instruments)
    print("Volumes:", volumes)
    print("Piano for part track:", piano_for_part_track)

    copy_midi2(input_midi, output_file, instruments, volumes, piano_for_part_track)
    print("END export_part")
    print("--------------------")
    print()


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
    parser.add_argument("output_dir", help="Output directory", default="./")
    parser.add_argument("part", help="Specific part name to process (default: process all parts)", nargs='?')
    args = parser.parse_args()

    output_dir = os.path.expanduser(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    settings = {**config, **load_settings(args.input_midi)}

    women = config['women_voices']
    men = config['men_voices']
    voices = {**women, **men}
    instruments = {}

    for v in women:
        instruments[v] = MIDI_INSTRUMENTS[settings['women_instrument']]

    for v in men:
        instruments[v] = MIDI_INSTRUMENTS[settings['men_instrument']]

    volumes = {}

    for v in voices.keys():
        print("Setting volume for {} to {}".format(v, settings['volumes']['default']))
        volumes[v] = get_default_volume_for_part(v, settings)

    # Set default volumes for special instruments.py
    volumes['Piano'] = settings['volumes']['piano']
    volumes['Wood Blocks'] = settings['volumes']['wood_blocks']

    input_midi = os.path.expanduser(args.input_midi)
    midi = MidiFile(input_midi)

    if args.part:
        output_file = get_output_file_name(input_midi, output_dir, voices[args.part])
        export_part(midi, output_file, args.part, instruments, volumes, settings['volumes']['part'],
                    settings['volumes']['part_piano'])
    else:
        for v in voices.keys():
            if find_track_by_name(midi, v):
                output_file = get_output_file_name(input_midi, output_dir, voices[v])
                export_part(midi, output_file, v, instruments.copy(), volumes.copy(), settings['volumes']['part'],
                            settings['volumes']['part_piano'])
            else:
                print(f"Skipping part {v} because it was not found in the input MIDI file")
        # Make an export for SATB
        for v in voices.keys():
            volumes[v] = settings['volumes']['satb']
        output_file = get_output_file_name(input_midi, output_dir, 'SATB')
        export_part(midi, output_file, 'SATB', instruments, volumes)


if __name__ == "__main__":
    main()
