import sys
from video_operations import frame_to_time, time_to_frame
from linked_list import LinkedList

def play_scene(self):
    
    start, end = self.current_node.data
    print (f"Playing segment {start}-{end}")
    if start is None or end is None:
        print ("Error: start is None or end is None")
        return

    self.play_and_pause_button.setEnabled(True)
    self.play_and_pause_button.setText("⏸")
    
    self.video_slider.setRange(start, end)

    # bind the vlc media player to the videoframe
    if sys.platform.startswith('linux'):  # for Linux using the X Server
        self.mediaplayer.set_xwindow(self.videoframe.winId())
    elif sys.platform == "win32":  # for Windows
        self.mediaplayer.set_hwnd(self.videoframe.winId()) # handle to the window
    elif sys.platform == "darwin":  # for MacOS
        self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

    start_time = frame_to_time(start, self.frame_rate)
    self.end_time = frame_to_time(end, self.frame_rate)

    if not self.mediaplayer.is_playing():
        self.mediaplayer.play()
    self.mediaplayer.set_time(start_time) # it only works if the video is playing and takes a float value (time) between 0 and 1

    self.timer.start(100) # check the video time every 100 ms

def play_next_scene(self):
    self.current_node = self.current_node.next # update the current node
    if self.current_node is None:
        print ("There are no more scenes")
        self.play_and_pause_button.setEnabled(False)
        self.play_and_pause_button.setText("Play/Pause")
        return
    play_scene(self)

