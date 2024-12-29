import os
import subprocess
import sys

def convert_midi_to_mp3(input_midi, output_dir):
    soundfont = "/home/janvanmansum/Music/Koor/ms_basic.sf3"
    output_wav = os.path.join(output_dir, os.path.basename(input_midi).replace('.mid', '.wav'))
    output_mp3 = os.path.join(output_dir, os.path.basename(input_midi).replace('.mid', '.mp3'))

    # Render MIDI to WAV
    subprocess.run(['fluidsynth', '-ni', soundfont, input_midi, '-F', output_wav, '-r', '44100'], check=True)

    # Convert WAV to MP3 using ffmpeg
    subprocess.run(['ffmpeg', '-y', '-i', output_wav, output_mp3], check=True)

    # Remove the intermediate WAV file
    os.remove(output_wav)

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_to_mp3.py <input_midi> <output_dir>")
        sys.exit(1)

    input_midi = sys.argv[1]
    output_dir = sys.argv[2]

    convert_midi_to_mp3(input_midi, output_dir)


if __name__ == "__main__":
    main()