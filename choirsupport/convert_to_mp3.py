import logging
import os
import subprocess
import argparse

from choirsupport.common import init


def convert_midi_to_mp3(input_midi: str, output_dir: str, soundfont: str = None):
    output_wav = os.path.join(output_dir, os.path.basename(input_midi).replace('.mid', '.wav'))
    output_mp3 = os.path.join(output_dir, os.path.basename(input_midi).replace('.mid', '.mp3'))

    # Render MIDI to WAV
    # TODO: Make the gain configurable
    subprocess.run(['fluidsynth', '-ni', '-g 0.5', soundfont, input_midi, '-F', output_wav, '-r', '44100'], check=True)

    # Convert WAV to MP3 using ffmpeg
    subprocess.run(['ffmpeg', '-y', '-i', output_wav, output_mp3], check=True)

    # Remove the intermediate WAV file
    os.remove(output_wav)


def main():
    config = init()
    logging.debug("Initialized configuration")
    parser = argparse.ArgumentParser(description="Convert MIDI files to MP3.")
    parser.add_argument('input_midi', type=str, help='The input MIDI file')
    parser.add_argument('output_dir', type=str, help='The output directory')

    args = parser.parse_args()

    input_midi = args.input_midi
    output_dir = os.path.expanduser(args.output_dir)

    # Check if input_midi exists
    if not os.path.exists(input_midi):
        # Process all parts
        input_dir = os.path.dirname(input_midi)
        basename = os.path.basename(input_midi)
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.startswith(basename) and file.endswith('.mid'):
                    full_path = os.path.join(root, file)
                    convert_midi_to_mp3(full_path, output_dir, config['soundfont'])
    else:
        # Process the single file
        convert_midi_to_mp3(input_midi, output_dir, config['soundfont'])


if __name__ == "__main__":
    main()