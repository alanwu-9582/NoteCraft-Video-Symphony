import os
from mido import MidiFile, MidiTrack, Message

def createDirectory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

class MidiSpliter:
    def __init__(self, file_path):
        self.midi_file = MidiFile(file_path)
        self.file_name = file_path.split("/")[-1][:-4]

    def splitMidi(self, note_proportion_filter=1, important_notes = []):
        output_notes_paths = []
        for i, track in enumerate(self.midi_file.tracks):
            current_time = 0
            msg_note_dic = {}
            
            for message in track:
                current_time += message.time
                if message.type in ['note_on', 'note_off']:
                    note = str(message.note)
                    
                    if note in msg_note_dic:
                        msg_note_dic[note].append([message, current_time])
                    else:
                        msg_note_dic[note] = [[message, current_time]]
            
            total_msg = sum([len(value) for value in msg_note_dic.values()])
            output_folder = f'assets/splited_midi/{self.file_name}/track_{i}'
            
            # 處理每一種音階
            for key, value in msg_note_dic.items():
                if (len(value) / total_msg) * 100 > note_proportion_filter or key in important_notes: 
                    saved_filename = self.processNote(value, f'{output_folder}')
                    output_notes_paths.append(saved_filename)

        return output_notes_paths

    # 處理單一音符
    def processNote(self, note_messages, output_folder):
        current_track = MidiTrack()
        current_midi = MidiFile()
        current_midi.tracks.append(current_track)
        
        last_time = 0
        last_msg = None
        for msg, current_time in note_messages:
            if last_msg and last_time and (last_msg.type != msg.type != 'note_off') and msg.velocity:
                wait_time = int((current_time - last_time) / 2)
                note_off = Message('note_off', note=last_msg.note, velocity=0, time=wait_time)
                current_track.append(note_off)
            else:
                wait_time = current_time - last_time
            
            msg.time = wait_time
            current_track.append(msg)
            last_time = current_time
            last_msg = msg
        
        if last_time != 0 and last_msg is not None:
            note_off = Message('note_off', note=last_msg.note, velocity=0, time=wait_time)
            current_track.append(note_off)
        
        createDirectory(output_folder)
        
        # 儲存處理後的MIDI檔案
        output_filename = f'{output_folder}/{self.file_name}_note-{note_messages[0][0].note}.mid'
        current_midi.save(output_filename)
        return output_filename