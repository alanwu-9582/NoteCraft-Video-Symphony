import os
from mido import MidiFile, MidiTrack, Message

# 檢查資料夾是否存在，如果不存在就建立
def create_directory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# 處理單一音符
def process_note(note_messages, output_folder):
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
    
    # 建立資料夾
    output_folder = f"midi_splited/{output_folder}"
    create_directory(output_folder)
    
    # 儲存處理後的MIDI檔案
    output_filename = f'{output_folder}/{Instrument}_note-{note_messages[0][0].note}.mid'
    current_midi.save(output_filename)

# 主程式
if __name__ == "__main__":
    # 設定MIDI檔案名稱
    Instrument = "GuitarToPiano1"

    note_len_filter = 3
    important_notes = []

    input_midi_file = f'midi_input/{Instrument}.mid'    
    midi_file = MidiFile(input_midi_file)
    
    # 處理每一個音軌
    for i, track in enumerate(midi_file.tracks):
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

        if len(midi_file.tracks) > 1:
            output_folder = f'{Instrument}/track_{i}'

        else:
            output_folder = Instrument
        
        # 處理每一種音階
        for key, value in msg_note_dic.items():
            if (len(value) / total_msg) * 100 > note_len_filter or key in important_notes: 
                process_note(value, f'{output_folder}')
