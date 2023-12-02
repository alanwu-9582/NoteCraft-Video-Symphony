import math
import os
from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips
import mido

def create_directory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def calculate_clip_durations(midi_path, bpm):
    midi_file = mido.MidiFile(midi_path)
    video_clips = []
    current_time_seconds = 0

    for track in midi_file.tracks:
        for msg in track:
            msg_time_seconds = mido.tick2second(msg.time, ticks_per_beat=midi_file.ticks_per_beat, tempo=mido.bpm2tempo(bpm))
            current_time_seconds += msg_time_seconds
            if msg.type == 'note_on':
                if msg.velocity > 0:
                    insert_clip_duration = [current_time_seconds]
                elif msg.velocity == 0:
                    insert_clip_duration.append(current_time_seconds)
                    video_clips.append(insert_clip_duration)

    return video_clips

def create_video_base_midi(Instrument, Note, bpm):
    video_path = f'video_elements/{Instrument}/{Instrument}_note-{Note}.mp4'
    midi_path = f'midi_splited/{Instrument}/{Instrument}_note-{Note}.mid'
    output_folder = f'video_combined/{Instrument}'

    video_clips = calculate_clip_durations(midi_path, bpm)
    input_clip = VideoFileClip(video_path)
    final_video_clips = []
    current_time = 0

    audio_clip = input_clip.audio
    volume_data = audio_clip.to_soundarray()
    max_volume_time = volume_data.argmax() / audio_clip.fps

    max_delay_time = math.inf

    if max_volume_time < max_delay_time:
        for start_time, end_time in video_clips:
            overflow = 0
            play_time = end_time - start_time
            if play_time > input_clip.duration:
                overflow = play_time - input_clip.duration
                play_time = input_clip.duration

            black_clip_replacement = ColorClip((input_clip.size[0], input_clip.size[1]), color=(0, 0, 0), duration=start_time - current_time)
            replacement_clip = input_clip.subclip(0, play_time)

            if black_clip_replacement.duration > 0:
                final_video_clips.append(black_clip_replacement)

            if replacement_clip.duration > 0:
                final_video_clips.append(replacement_clip)

            current_time = end_time + overflow

        create_directory(output_folder)
        final_video = concatenate_videoclips(final_video_clips, method="compose")
        final_video.write_videofile(f'{output_folder}/{Instrument}_note-{Note}.mp4', codec='libx264', fps=30)

    else:
        print(f"警告: 節奏過慢! {max_volume_time:.2f} >= {max_delay_time}")
        
    input_clip.close()

if __name__ == "__main__":
    Instrument = "MainPiano"
    Notes = [60, 61, 63, 65, 67, 68, 70, 72, 73, 75]
    bpm = 123
    
    for Note in Notes:
        create_video_base_midi(Instrument, Note, bpm)