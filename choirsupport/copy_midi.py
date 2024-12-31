import argparse
import logging
import os.path

from mido import MidiFile, MidiTrack, MetaMessage, Message

channel_msg_types = ['note_on', 'note_off', 'control_change', 'polytouch', 'pitchwheel', 'aftertouch']


def log():
    return logging.getLogger(__name__)


def copy_track(track, new_instrument=None, new_volume=None):
    log().debug("Copying track %s with new_instrument = %s, new_volume = %s", track.name, new_instrument, new_volume)
    new_track = MidiTrack()
    for msg in track:
        if msg.type == 'program_change' and new_instrument is not None:
            new_track.append(msg.copy(program=new_instrument))
        elif msg.type == 'control_change' and msg.control == 7 and new_volume is not None:
            new_track.append(msg.copy(value=new_volume))
        else:
            new_track.append(msg.copy())
    return new_track


def copy_track_to_new_channel(track, new_name, new_instrument=None, new_volume=None, new_channel=None):
    log().debug("Copying track %s with new_name = %s, new_instrument = %s, new_volume = %s, new_channel = %s",
                track.name, new_name, new_instrument, new_volume, new_channel)
    new_track = MidiTrack()
    new_track.append(MetaMessage('track_name', name=new_name, time=0))
    for msg in track:
        if msg.type == 'program_change' and new_instrument is not None:
            new_track.append(msg.copy(program=new_instrument, channel=new_channel))
        elif msg.type == 'control_change' and msg.control == 7 and new_volume is not None:
            new_track.append(msg.copy(value=new_volume, channel=new_channel))
        elif msg.type in channel_msg_types:
            new_track.append(msg.copy(channel=new_channel))
        else:
            new_track.append(msg.copy())
    return new_track


def copy_midi(midi: MidiFile, instruments: dict, volumes: dict, extra_track=None):
    new_midi = MidiFile()

    for i, track in enumerate(midi.tracks):
        instrument = None
        if track.name in instruments:
            log().debug(f"Changing instrument of track {track.name} to  {instruments[track.name]}")
            instrument = instruments[track.name]
        volume = None
        if track.name in volumes:
            log().debug(f"Changing volume of track {track.name} to {volumes[track.name]}")
            volume = volumes[track.name]
        new_midi.tracks.append(copy_track(track, instrument, volume))

    if extra_track is not None:
        log().debug(f"Adding extra track: {extra_track['name']}")
        new_midi.tracks.append(
            copy_track_to_new_channel(track=find_track_by_name(new_midi, extra_track['melody_from']),
                                      new_name=extra_track['name'],
                                      new_instrument=extra_track['instrument'],
                                      new_volume=extra_track['volume'],
                                      new_channel=find_unused_channel(midi)))
    return new_midi


def copy_midi_file(input_file: str, output_file: str, instruments: dict, volumes: dict, extra_track=None):
    log().debug(f"Input file: {input_file}")
    midi = MidiFile(input_file)
    midi_copy = copy_midi(midi, instruments, volumes, extra_track)
    midi_copy.save(output_file)
    log().info("Saved MIDI file to %s", output_file)


def find_unused_channel(midi):
    channels = set(range(16))
    for track in midi.tracks:
        for msg in track:
            if msg.type in channel_msg_types:
                channels.discard(msg.channel)
    return channels.pop() if channels else None


def find_track_by_name(midi, name):
    for i, track in enumerate(midi.tracks):
        for msg in track:
            if msg.type == 'track_name' and msg.name == name:
                return track
    return None


def main():
    parser = argparse.ArgumentParser(description='Copy a MIDI file')
    parser.add_argument('input_file', help='Input MIDI file')
    parser.add_argument('output_file', help='Output MIDI file')
    args = parser.parse_args()

    # TODO: Make these configurable
    instruments = {
        'Soprano': 53,
        'Mezzo-soprano': 53,
        'Alto': 53,
        'Alto 1': 53,
        'Alto 2': 53,
        'Tenor': 52,
        'Tenor 1': 52,
        'Tenor 2': 52,
        'Baritone': 52,
        'Bass': 52,
    }

    volumes = {
        'Soprano': 70,
        'Mezzo-soprano': 70,
        'Alto': 70,
        'Alto 1': 70,
        'Alto 2': 70,
        'Tenor': 70,
        'Tenor 1': 70,
        'Tenor 2': 70,
        'Baritone': 127,
        'Bass': 127,
        'Wood Blocks': 70,
        'Slap': 127
    }

    # extra_track = None
    extra_track = {
        'name': 'Piano',
        'instrument': 0,
        'volume': 127,
        'melody_from': 'Bass'
    }

    copy_midi_file(os.path.expanduser(args.input_file), os.path.expanduser(args.output_file), instruments, volumes,
                   extra_track)


if __name__ == '__main__':
    main()
