import json
import threading

import tkinter as tk
from tkinter import ttk, filedialog
from libs.LogTextbox import LogTextbox

from Constants import *
from MidiSpliter import MidiSpliter
from MidiVideoCombiner import MidiVideoCombiner

class MidiVideoComposerGUI:
    def __init__(self, master):
        self.master = master
        self.midi_spliters = []

        self.intitializeData()
        self.intitializeUI()

    def intitializeData(self):
        with open(f'assets/data.json', 'r', encoding='utf-8') as jfile:
            self.data = json.load(jfile)

        self.splited_midi = self.data['splited_midi']
        self.splited_midi_values = []
        for splited_notes_paths in self.splited_midi.values():
            self.splited_midi_values += splited_notes_paths

        self.splited_midi_names = [splited_midi_value.split('/')[-1][:-4] for splited_midi_value in self.splited_midi_values]

        self.imported_midi = []

    def writeData(self):
        self.data['video_sample_path'] = self.video_sample_path.get()
        with open(f'assets/data.json', 'w', encoding='utf-8') as jfile:
            json.dump(self.data, jfile, ensure_ascii=False, indent=4)

    def intitializeUI(self):
        self.master.geometry('720x185')
        self.master.title("Midi Video Composer")
        # self.master.iconbitmap("assets/icon.ico")
        self.master.config(bg="#eeeeee", padx = 5, pady = 5)

        self.createFrames()
        self.createObjects()
        self.createFunctionButtons()

    def createFrames(self):
        self.info_display_frame = tk.Frame(self.master)
        self.info_display_frame.grid(row=0, column=0)
        self.info_display_frame.config(bg="#cccccc", padx=2, pady=5)

        self.info_display_mid_frame = tk.Frame(self.info_display_frame)
        self.info_display_mid_frame.grid(row=0, column=1)
        self.info_display_mid_frame.config(bg="#cccccc", padx=2, pady=5)

        self.display_input_frame = tk.Frame(self.info_display_mid_frame)
        self.display_input_frame.grid(row=1, column=0)
        self.display_input_frame.config(bg="#cccccc", padx=2, pady=5)

        self.display_btn_frame = tk.Frame(self.display_input_frame)
        self.display_btn_frame.grid(row=3, column=0)
        self.display_btn_frame.config(bg="#cccccc", padx=2, pady=5)

        self.dashboard_frame = tk.Frame(self.master)
        self.dashboard_frame.grid(row=1, column=0)
        self.dashboard_frame.config(bg="#b9b9b9", padx=2, pady=5)

    def createObjects(self):
        self.log = LogTextbox(self.info_display_frame, width=22,  height=8, font=("System", 10), relief="solid")
        self.log.grid(row=0, column=0, padx=4, pady=2)

        self.display_info = tk.StringVar()
        Label = tk.Label(self.info_display_mid_frame, textvariable=self.display_info, text="", font=("Microsoft JhengHei UI", 12), anchor="n", width=32, bg="#c2c2c2")
        Label.grid(row=0, column=0, padx=3)

        self.imported_midi_combobox = ttk.Combobox(self.display_input_frame, width=32)
        self.imported_midi_combobox.grid(row=0, column=0, padx=3)

        self.important_notes = tk.StringVar()
        Entry = ttk.Entry(self.display_input_frame,  textvariable=self.important_notes, width=34)
        Entry.grid(row=1, column=0, padx=3, pady=2)

        self.note_proportion_filter = tk.StringVar()
        Spinbox = tk.Spinbox(self.display_input_frame, from_=0, to=100, textvariable=self.note_proportion_filter)
        Spinbox.config(width=10)
        Spinbox.grid(row=1, column=1)
        self.note_proportion_filter.set(1)

        self.video_sample_path = tk.StringVar()
        Entry = ttk.Entry(self.display_input_frame,  textvariable=self.video_sample_path, width=34)
        Entry.grid(row=2, column=0, padx=3, pady=2)
        self.video_sample_path.set(self.data['video_sample_path'])

        self.video_sample_original_pitch = tk.StringVar()
        Spinbox = tk.Spinbox(self.display_input_frame, from_=21, to=108, textvariable=self.video_sample_original_pitch)
        Spinbox.config(width=10)
        Spinbox.grid(row=2, column=1)
        self.video_sample_original_pitch.set(60)

        self.splited_strvar = tk.StringVar()
        self.splited_listbox = tk.Listbox(self.info_display_frame,  listvariable=self.splited_strvar, font=("System", 10), width=20, height=8, relief='solid', selectmode=tk.EXTENDED)
        self.splited_listbox.grid(row=0, column=2, padx=4, pady=2)
        self.splited_strvar.set(self.splited_midi_names)

    def createFunctionButtons(self):
        DEAFULT_BUTTON_WIDTH = 10
        DEAFULT_SMALLER_BUTTON_WIDTH = 10

        self.splitMidi_btn = ttk.Button(self.display_input_frame, text="分割 midi", width=DEAFULT_SMALLER_BUTTON_WIDTH, command=self.splitMidi)
        self.splitMidi_btn.grid(row=0, column=1, padx=1, pady=2)

        self.importMidi_btn = ttk.Button(self.display_btn_frame, text="匯入 midi", width=DEAFULT_BUTTON_WIDTH, command=self.importMidi)
        self.importMidi_btn.grid(row=0, column=0, padx=1, pady=2)

        self.importVideoSample_btn = ttk.Button(self.display_btn_frame, text="匯入樣本", width=DEAFULT_BUTTON_WIDTH, command=self.importVideoSample)
        self.importVideoSample_btn.grid(row=0, column=1, padx=1, pady=2)

        self.combineMidiVideo_btn = ttk.Button(self.display_btn_frame, text="合成影片", width=DEAFULT_BUTTON_WIDTH, command=self.combineMidiVideo)
        self.combineMidiVideo_btn.grid(row=0, column=2, padx=1, pady=2)

    def splitMidi(self):
        selection = self.imported_midi_combobox.current()
        note_proportion_filter = int(self.note_proportion_filter.get())
        important_notes = list(map(int, self.important_notes.get().split()))

        if selection == -1:
            return
        
        splited_notes = self.midi_spliters[selection].splitMidi(note_proportion_filter=note_proportion_filter, important_notes=important_notes)
        midi_file_name = self.midi_spliters[selection].file_name
        self.splited_midi[midi_file_name] = [splited_note for splited_note in splited_notes]
        self.splited_midi_values = []
        for splited_notes_paths in self.splited_midi.values():
            self.splited_midi_values += splited_notes_paths

        self.splited_midi_names = [splited_midi_value.split('/')[-1][:-4] for splited_midi_value in self.splited_midi_values]
        self.splited_strvar.set(self.splited_midi_names)
        
        self.writeData()

        self.log.updateLog(f'Splited {midi_file_name}', LOG_DONE_COLOR)

    def importMidi(self):
        file_path = filedialog.askopenfilename(title="Import Midi", filetypes= [("Midi files","*.mid")])
        if file_path:
            midi_spliter = MidiSpliter(file_path)
            if midi_spliter.file_name in self.imported_midi:
                self.log.updateLog(f'Already Loaded {midi_spliter.file_name}', LOG_WARN_COLOR)
                return

            self.midi_spliters.append(midi_spliter)
            self.imported_midi.append(midi_spliter.file_name)
            self.log.updateLog(f'Loaded {midi_spliter.file_name}', LOG_DONE_COLOR)
            self.imported_midi_combobox.config(values=self.imported_midi)

    def importVideoSample(self):
        file_path = filedialog.askopenfilename(title="Import Video Sample", filetypes= [("Mp4 files","*.mp4")])
        if file_path:
            self.video_sample_path.set(file_path)
            self.writeData()
            self.log.updateLog(f'Set Sample:', LOG_DONE_COLOR)
            self.log.updateLog(f'  {file_path.split("/")[-1]}')

    def combineMidiVideo(self):
        selections = self.splited_listbox.curselection()
        if len(selections) <= 0:
            return
        
        def combineMidiVideo_thread(): 
            video_sample_pitch = int(self.video_sample_original_pitch.get())
            video_sample_path = self.video_sample_path.get()
            self.combineMidiVideo_btn.config(state=tk.DISABLED)
            
            for selection in selections:
                midi_name = self.splited_midi_names[selection].split("_")[0]
                midi_pitch = int(self.splited_midi_names[selection].split("-")[-1])
                self.log.updateLog(f'Combining {midi_name}-{midi_pitch}', LOG_PROCESS_COLOR)

                VideoCombiner = MidiVideoCombiner(
                    main_midi_name=midi_name,
                    video_sample_path=video_sample_path, 
                    midi_file_path=self.splited_midi_values[selection], 
                    bpm=123
                )

                VideoCombiner.createVideoBaseMidi()

                if midi_pitch != video_sample_pitch:
                    self.log.updateLog(f'Adjusting {midi_name}-{midi_pitch}', LOG_PROCESS_COLOR)
                    VideoCombiner.adjustPitch(midi_pitch, video_sample_pitch)

            self.log.updateLog(f'Finish output', LOG_DONE_COLOR)
            self.combineMidiVideo_btn.config(state=tk.NORMAL)
        
        tdownload = threading.Thread(target=combineMidiVideo_thread)
        tdownload.start()
            
if __name__ == "__main__":
    root = tk.Tk()
    gui = MidiVideoComposerGUI(root)
    root.mainloop()