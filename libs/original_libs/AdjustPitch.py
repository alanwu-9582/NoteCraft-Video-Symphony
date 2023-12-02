import librosa
import librosa.display
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np

def replace_audio(video_path, audio_path, output_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

def extract_audio(video_path, audio_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path, codec='pcm_s16le')

def adjust_to_midi_pitch_librosa(input_audio, target_midi_pitch, previous_midi_pitch=60, output_audio='adjusted_audio.wav'):
    y, sr = librosa.load(input_audio, sr=None)
    semitones_to_adjust = target_midi_pitch - previous_midi_pitch  # 60 是中央的C音的MIDI值
    y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=semitones_to_adjust)
    sf.write(output_audio, y_shifted, sr)

def adjust_pitch(Instrument, Note):
    video_path = f'video_combined/{Instrument}/{Instrument}_note-{Note}.mp4'
    output_path = f'audio_adjusted/{Instrument}/{Instrument}_note-{Note}.wav'

    temp_audio_path = 'temp_audio.wav'
    extract_audio(video_path, temp_audio_path)
    adjust_to_midi_pitch_librosa(temp_audio_path, Note, output_audio=output_path)

if __name__ == "__main__":
    Instrument = "MainPiano"
    Notes = [60, 61, 63, 65, 67, 68, 70, 72, 73, 75]

    for Note in Notes:
        adjust_pitch(Instrument, Note)

