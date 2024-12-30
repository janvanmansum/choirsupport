import logging
import os
import subprocess
import argparse

from choirsupport.common import init


def convert_midi_to_mp3(input_midi: str, output_dir: str, soundfont: str = None):
    output_wav = os.path.join(output_dir, os.path.basename(input_midi).replace('.mid', '.wav'))
    output_mp3 = os.path.join(output_dir, os.path.basename(input_midi).replace('.mid', '.mp3'))

    # Render MIDI to WAV
    subprocess.run(['fluidsynth', '-ni', soundfont, input_midi, '-F', output_wav, '-r', '44100'], check=True)

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

    convert_midi_to_mp3(args.input_midi, args.output_dir, config['soundfont'])


if __name__ == "__main__":
    main()
