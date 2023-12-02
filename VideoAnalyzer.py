import os
from moviepy.video.io.VideoFileClip import VideoFileClip

def createDirectory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

class VideoAnalyzer:
    def __init__(self, volume_threshold=0.01, min_time=0.5):
        self.volume_threshold = volume_threshold
        self.min_time = min_time

    def extractAudioSegments(self, video_path, output_path='audio_segments.txt'):
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_frames = audio_clip.iter_frames()
        audio_segments = []
        segment_start = None
        current_time = 0
        
        for frame in audio_frames:
            volume = sum(abs(frame))
            
            if volume > self.volume_threshold:
                if segment_start is None:
                    segment_start = current_time

            else:
                if segment_start is not None:
                    segment_end = current_time
                    audio_segments.append((segment_start, segment_end))
                    segment_start = None

            current_time += 1 / audio_clip.fps

        merged_segments = []
        if audio_segments:
            merged_segments.append(audio_segments[0])
            for i in range(1, len(audio_segments)):
                prev_end = merged_segments[-1][1]
                current_start = audio_segments[i][0]
                
                if current_start - prev_end < self.min_time:
                    merged_segments[-1] = (merged_segments[-1][0], audio_segments[i][1])
                else:
                    merged_segments.append(audio_segments[i])

        def time2Prtime(time):
            msecond = (time % 1) * 30 / 100
            long_second = time - time % 1
            second = long_second % 60
            minute = ((long_second - second) // 60) * 100 if (long_second - second) > 0 else 0

            return minute + second + msecond
            

        with open(output_path, 'w') as file:
            for segment in merged_segments:
                start_time, end_time = segment

                start_time = time2Prtime(start_time)
                end_time = time2Prtime(end_time)

                file.write(f"{start_time:.2f} - {end_time:.2f}\n")

        video_clip.close()
        audio_clip.close()

if __name__ == '__main__':
    notes = [60, 61, 63, 65, 67, 68, 70, 72, 73, 75]
    instrument = 'MainPiano'

    video_analyzer = VideoAnalyzer()

    for note in notes:
        print(f'Analyzing {instrument} note {note}...')

        video_path = f'assets/adjusted_video/{instrument}/{instrument}_note-{note}.mp4'
        output_path = f'assets/video_analyze_report/{instrument}/{instrument}_note-{note}.txt'

        video_analyzer.extractAudioSegments(video_path, output_path)
