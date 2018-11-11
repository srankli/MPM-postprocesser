import time
import os
# ImageIO
import imageio
# PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# VTK
from VTKGraph import VTKGraph

# Get the time length of animation
class GetAnimationTimeLength(QDialog):
    def __init__(self, parent = None):
        super(GetAnimationTimeLength, self).__init__(parent)
        self.setWindowTitle("Animation time (s)")
        self.resize(160, 40)
        self.time_value = QLineEdit(self)
        self.time_value.setGeometry(QRect(10, 10, 70, 20))
        self.ok_button = QPushButton(self)
        self.ok_button.setGeometry(QRect(90, 10, 60, 20))
        self.ok_button.setText("OK")
        self.ok_button.clicked.connect(self.accept)

    def getValueText(self):
        return self.time_value.text()

# Thread for creating animation
# class PlayAnimationThread(QThread):
#     def __init__(self, ani_win):
#         super(PlayAnimationThread, self).__init__()
#         self.display_scene_signal = pyqtSignal(int)
#         self.ani_win = ani_win
#         self._isStopped = False

#     def setStop(self):
#         self._isStopped = True

#     def run(self):
#         play_this_frame = True
#         if self.ani_win.cur_animation_frame < self.ani_win.time_frame_num:
#             prev_time = self.ani_win.time_frame[self.ani_win.cur_animation_frame]
#         while not self._isStopped:
#             if play_this_frame:
#                 # wait until the window lock has been released
#                 self.ani_win.vtk_ani_lock.lock()
#                 # Tell window to render frame
#                 self.display_scene_signal.emit(self.ani_win.cur_animation_frame)
#                 ani_time_inc = 0.0
#                 prev_ani_frame_time = time.time()
#             # next frame
#             self.ani_win.cur_animation_frame += 1
#             # check if finish the animation
#             if self.ani_win.cur_animation_frame >= self.ani_win.time_frame_num:
#                 self.ani_win.disablePauseAndContinue()
#                 break
#             # get time increment
#             next_time = self.ani_win.time_frame[self.ani_win.cur_animation_frame]
#             time_inc = next_time - prev_time
#             ani_time_inc += time_inc / self.ani_win.total_time * self.ani_win.animation_time
#             prev_time = next_time
#             # sleep enough time
#             # maximum play 30 frame per second
#             if ani_time_inc < 1.0 / 30.0:
#                 play_this_frame = False
#             else:
#                 play_this_frame = True
#                 sleep_time = ani_time_inc - time.time() + prev_ani_frame_time
#                 if sleep_time > 0:
#                     time.sleep(sleep_time)
#         # finish playing
#         self.ani_win.vtk_win_lock.unlock()

#####################################################
class AnimationGraph(VTKGraph):
    display_scene_signal = pyqtSignal(int)
    def __init__(self, time_frame, win_name = "AnimationGraph", parent = None):
        super(AnimationGraph, self).__init__(win_name, parent)
        # variables for animation
        self.ani_playing = False
        #self.ani_cur_time = 0.0
        self.data_cur_time = 0.0
        self.ani_total_time = 0.0
        self.data_total_time = time_frame[-1]
        self.ani_data_ratio = 0.0 # = self.ani_total_time / self.data_total_time
        self.time_frame = time_frame
        self.cur_frame = 0
        self.frame_num = len(time_frame)
        if self.frame_num <= 0:
            self.printMsg("No field data available.")
        self.display_scene_signal.connect(self._createScene_ani)
        self.ani_timer = QTimer()
        self.ani_timer.setSingleShot(True)
        self.ani_timer.timeout.connect(self.animationScheduler)
        # set time list of this field output
        self.setTimeList(time_frame)
        self.time_list.itemDoubleClicked.connect(self.displayDeformation)
        if self.frame_num > 0:
            self.time_list.setCurrentRow(0)
            self.displayDeformation()
        # Menu bar
        # field_menu = self.menuBar().addMenu("D&isplay")
        # display_deformation_action = QAction("Deformation", self)
        # display_deformation_action.triggered.connect(self.displayDeformation)
        # field_menu.addAction(display_deformation_action)
        animation_menu = self.menuBar().addMenu("A&nimation")
        # set time
        set_time_action = QAction("Set time", self)
        set_time_action.triggered.connect(self.setAnimationTime)
        animation_menu.addAction(set_time_action)
        #
        animation_menu.addSeparator()
        # play
        play_animation_action = QAction("Play", self)
        play_animation_action.triggered.connect(self.playAnimation)
        animation_menu.addAction(play_animation_action)
        # pause
        self.pause_animation_action = QAction("Pause", self)
        self.pause_animation_action.triggered.connect(self.pauseAnimation)
        animation_menu.addAction(self.pause_animation_action)
        # continue
        self.continue_animation_action = QAction("Continue", self)
        self.continue_animation_action.triggered.connect(self.continueAnimation)
        animation_menu.addAction(self.continue_animation_action)
        # stop
        self.stop_animation_action = QAction("Stop", self)
        self.stop_animation_action.triggered.connect(self.stopAnimation)
        animation_menu.addAction(self.stop_animation_action)
        self.disableAniButtons()
        #
        animation_menu.addSeparator()
        # export animation
        export_animatin_action = QAction("Export Animation", self)
        export_animatin_action.triggered.connect(self.exportAnimation)
        animation_menu.addAction(export_animatin_action)

    # This function needed to be redefined in subclass
    def _createScene(self, frame_index):
        pass
    
    def displayDeformation(self):
        selected_frame_index = self.time_list.currentRow()
        if selected_frame_index < 0:
            return
        # pause animation here
        self.pauseAnimation()
        # display deformation
        if not self.vtk_win_lock.tryLock():
            return
        self._createScene(selected_frame_index)
        self.vtk_win_lock.unlock()

    def setAnimationTime(self):
        get_time_dialog = GetAnimationTimeLength(self)
        get_time_dialog.exec()
        ani_time = get_time_dialog.getValueText()
        try:
            ani_time = float(ani_time)
        except ValueError:
            self.printMsg("Should input float")
            return -1
        else:
            if ani_time < 0.5:
                self.printMsg("Should input time > 0.5s")
                return -1
            self.ani_total_time = ani_time
            return 0

    def _createScene_ani(self, frame_index):
        if not self.vtk_win_lock.tryLock():
            return
        self._createScene(frame_index)
        self.vtk_win_lock.unlock()

    def enableAniButtons(self):
        # enable pause Animation and continue Animation button
        self.pause_animation_action.setEnabled(True)
        self.continue_animation_action.setEnabled(True)
        self.stop_animation_action.setEnabled(True)

    def disableAniButtons(self):
        # disable pause Animation and continue Animation button
        self.pause_animation_action.setEnabled(False)
        self.continue_animation_action.setEnabled(False)
        self.stop_animation_action.setEnabled(False)

    def animationScheduler(self):
        # if animation needed to be stopped
        if not self.ani_playing:
            return
        # init vars, unit: s
        ani_time_inc = 0.0
        prev_real_time = time.time()
        # emit signal to display scene
        self.display_scene_signal.emit(self.cur_frame)
        self.data_cur_time = self.time_frame[self.cur_frame]
        #print(self.data_cur_time)
        # find the next frame to be displayed
        # maximum frame rate 30 frame/s
        while ani_time_inc < 1.0 / 30.0:
            self.cur_frame += 1
            if self.cur_frame >= self.frame_num:
                self.stopAnimation()
                return
            # get time increment
            data_next_time = self.time_frame[self.cur_frame]
            ani_time_inc = (data_next_time - self.data_cur_time) * self.ani_data_ratio
        # calculate next time to called this scheduler and start taking rest :)
        sleep_time = ani_time_inc - (time.time() - prev_real_time)
        if sleep_time < 0:
            sleep_time = 0
        self.ani_timer.start(sleep_time * 1000) # convert unit into ms

    def playAnimation(self):
        if self.frame_num <= 0:
            self.printMsg("No data available for display.")
            return
        # pause existing animation
        self.pauseAnimation()
        # check animation time
        if self.ani_total_time < 0.5:
            if self.setAnimationTime():
                return
        # play animation
        self.cur_frame = 0
        self.ani_data_ratio = self.ani_total_time / self.data_total_time
        self.ani_playing = True
        self.animationScheduler()
        # enable pause and continue buttons
        self.enableAniButtons()

    def pauseAnimation(self):
        # see if animation is playing
        if self.ani_playing:
            self.ani_playing = False
            self.ani_timer.stop()

    def continueAnimation(self):
        self.ani_playing = True
        self.animationScheduler()

    def stopAnimation(self):
        self.disableAniButtons()
        self.pauseAnimation()
        self._createScene_ani(0)

    # Create gif animation
    def _exportGIFAnimation(self, gif_filename, gif_duration, max_frame_rate = 60.0):
        if self.frame_num <= 0:
            return
        png_filenames = []
        frame_durations = []
        png_images = []
        cur_frame_index = 0
        gif_data_time_ratio = gif_duration / self.data_total_time
        min_frame_duration = 1.0 / max_frame_rate
        isFrame = True
        # Create png and calculate frame duration for each frames
        while True:
            if isFrame:
                # create png
                png_filename = "Temporary_PNG_Image_for_GIF_Animation_Index_" \
                                + str(cur_frame_index) + ".png"
                png_filenames.append(png_filename)
                self._createScene(cur_frame_index)
                self._exportPNGImage(png_filename)
                png_images.append(imageio.imread(png_filename))
                prev_data_time = self.time_frame[cur_frame_index]
            # next frame
            cur_frame_index += 1
            if cur_frame_index >= self.frame_num:
                frame_durations.append(frame_durations[-1])
                break
            data_time_inc = self.time_frame[cur_frame_index] - prev_data_time
            gif_time_inc = data_time_inc * gif_data_time_ratio
            if gif_time_inc < min_frame_duration:
                isFrame = False
            else:
                isFrame = True
                frame_durations.append(gif_time_inc)
        # Create gif animation
        if self.frame_num > 0:
            imageio.mimsave(gif_filename, png_images, duration = frame_durations)
        # Delete all png
        for png_filename in png_filenames:
            os.remove(png_filename)

    def exportAnimation(self):
        # pause existing animation
        self.pauseAnimation()
        # Get animation time
        if self.ani_total_time < 0.5:
            if self.setAnimationTime():
                return
        # Get Filename
        file_path, file_type = QFileDialog.getSaveFileName(self,      
            "Output Figure", "./", "GIF Image Files (*.gif);;All Files (*)")
        if file_path == '':
            return
        # because self._createScene use the window,
        # the main window have to be locked.
        if not self.vtk_win_lock.tryLock(): 
            return
        self._exportGIFAnimation(file_path, self.ani_total_time)
        self.vtk_win_lock.unlock()

