import math
import os
import mido
import librosa
import librosa.display
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip, concatenate_videoclips

def createDirectory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

class MidiVideoCombiner:
    def __init__(self, main_midi_name, video_sample_path, midi_file_path, bpm):
        self.bpm = bpm
        self.main_midi_name = main_midi_name
        self.midi_file_path = midi_file_path
        self.midi_file = mido.MidiFile(midi_file_path)
        self.video_clips = self.calculateClipDurations(bpm)
        self.video_sample_path = video_sample_path
        self.input_clip = VideoFileClip(video_sample_path)        
        
    def calculateClipDurations(self, bpm):
        video_clips = []
        current_time_seconds = 0

        for track in self.midi_file.tracks:
            for msg in track:
                msg_time_seconds = mido.tick2second(msg.time, ticks_per_beat=self.midi_file.ticks_per_beat, tempo=mido.bpm2tempo(bpm))
                current_time_seconds += msg_time_seconds
                if msg.type == 'note_on':
                    if msg.velocity > 0:
                        insert_clip_duration = [current_time_seconds]
                    elif msg.velocity == 0:
                        insert_clip_duration.append(current_time_seconds)
                        video_clips.append(insert_clip_duration)

        return video_clips
    
    def createVideoBaseMidi(self):
        final_video_clips = []
        current_time = 0

        audio_clip = self.input_clip.audio
        volume_data = audio_clip.to_soundarray()
        max_volume_time = volume_data.argmax() / audio_clip.fps

        max_delay_time = math.inf

        if max_volume_time < max_delay_time:
            for start_time, end_time in self.video_clips:
                overflow = 0
                play_time = end_time - start_time
                if play_time > self.input_clip.duration:
                    overflow = play_time - self.input_clip.duration
                    play_time = self.input_clip.duration

                black_clip_replacement = ColorClip((self.input_clip.size[0], self.input_clip.size[1]), color=(0, 0, 0), duration=start_time - current_time)
                replacement_clip = self.input_clip.subclip(0, play_time)

                if black_clip_replacement.duration > 0:
                    final_video_clips.append(black_clip_replacement)

                if replacement_clip.duration > 0:
                    final_video_clips.append(replacement_clip)

                current_time = end_time + overflow

            output_folder = f'assets/combined_video/{self.main_midi_name}'
            createDirectory(output_folder)
            final_video = concatenate_videoclips(final_video_clips, method="compose")
            self.combined_file = f'{output_folder}/{self.midi_file_path.split("/")[-1][:-4]}.mp4'
            final_video.write_videofile(self.combined_file, codec='libx264', fps=30)

        else:
            print(f"警告: 節奏過慢! {max_volume_time:.2f} >= {max_delay_time}")
            
        self.input_clip.close()

    def replacAudio(self, video_path, audio_path, output_folder_path):
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        video_clip = video_clip.set_audio(audio_clip)
        createDirectory(output_folder_path)
        output_path = f'{output_folder_path}/{self.midi_file_path.split("/")[-1][:-4]}.mp4'
        video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30)

    def extractAudio(self, video_path, audio_path):
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path, codec='pcm_s16le')

    def adjustPitchLibrosa(self, input_audio, target_pitch, previous_pitch=60, output_audio='temp_adjusted_audio.wav'):
        y, sr = librosa.load(input_audio, sr=None)
        semitones_to_adjust = target_pitch - previous_pitch  # 60 是中央的C音的MIDI值
        y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=semitones_to_adjust)
        sf.write(output_audio, y_shifted, sr)

    def adjustPitch(self, pitch: int, previous_pitch=60):
        temp_audio_path = 'temp_audio.wav'
        adjusted_audio_path = 'temp_adjusted_audio.wav'
        self.extractAudio(self.combined_file, temp_audio_path)
        self.adjustPitchLibrosa(input_audio=temp_audio_path, target_pitch=pitch, previous_pitch=previous_pitch, output_audio=adjusted_audio_path)
        output_folder_path = f'assets/adjusted_video/{self.main_midi_name}'
        self.replacAudio(self.combined_file, adjusted_audio_path, output_folder_path)

        