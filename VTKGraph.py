# PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# VTK
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from ImageSizeDialog import ImageSizeDialog

class VTKGraph(QMainWindow):
    def __init__(self, win_name = "VTK Graph", parent = None):
        super(VTKGraph, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        # lock for window widget
        self.vtk_win_lock = QMutex()
        # setup window
        self.setWindowTitle(win_name)
        screen_x_pos, screen_y_pos, screen_width, screen_height = QDesktopWidget().geometry().getRect()
        self.window_width = screen_width * 0.5
        self.window_height = screen_height * 0.5
        self.resize(self.window_width, self.window_height)
        self.move((screen_width - self.window_width) / 2,  (screen_height - self.window_height) / 2)
        # Note that this winodw should be modaless
        #self.setWindowModality(Qt.ApplicationModaless)
        # Destructed when closed
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Menu Bar
        file_menu = self.menuBar().addMenu("File(&F)")
        resize_action = QAction("resize image", self)
        resize_action.triggered.connect(self.resizeImage)
        file_menu.addAction(resize_action)
        export_action = QAction("export image", self)
        export_action.triggered.connect(self.exportImage)
        file_menu.addAction(export_action)
        # Central Widget
        main_splitter = QSplitter(self)
        main_splitter.setOrientation(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        # Frame for content structure of hdf5 file
        left_frame = QFrame(main_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.addWidget(left_frame)
        left_frame_layout = QVBoxLayout()
        left_frame.setLayout(left_frame_layout)
        time_label = QLabel(left_frame)
        time_label.setText("Time")
        left_frame_layout.addWidget(time_label)
        left_frame_layout.setStretchFactor(time_label, 1)
        self.time_list = QListWidget(left_frame)
        left_frame_layout.addWidget(self.time_list)
        left_frame_layout.setStretchFactor(self.time_list, 25)
        # Create the VTK widget
        right_frame = QFrame(main_splitter)
        main_splitter.setStretchFactor(1, 5)
        main_splitter.addWidget(right_frame)
        right_frame_layout = QVBoxLayout()
        right_frame.setLayout(right_frame_layout)
        self.vtk_widget = QVTKRenderWindowInteractor(right_frame)
        right_frame_layout.addWidget(self.vtk_widget)
        #FigureCanvas.setSizePolicy(self.plot_widget, QSizePolicy.Expanding, QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self.plot_widget)
        # Status Bar
        self.statusBar()

    def printMsg(self, msg_str):
        self.statusBar().showMessage(msg_str)

    def getInteractorWidget(self):
        return self.vtk_widget
    
    def getRenderWindow(self):
        return self.vtk_widget.GetRenderWindow()

    def setTimeList(self, time_data):
        for t in time_data:
            self.time_list.addItem(str(t))

    def resizeImage(self):
        main_x_pos, main_y_pox, main_x_len, main_y_len = self.geometry().getRect()
        fig_x_pos, fig_y_pos, fig_x_len, fig_y_len = self.vtk_widget.geometry().getRect()
        get_size_dialog = ImageSizeDialog(self, fig_x_len, fig_y_len)
        if (get_size_dialog.exec()):
            fig_x, fig_y = get_size_dialog.getXYText()
            try:
                fig_x = int(fig_x)
                fig_y = int(fig_y)
            except ValueError:
                self.printMsg("Should input integer.")
            else:
                if (fig_x != 0 and fig_y != 0):
                    # set size of figure
                    self.setGeometry(main_x_pos, main_y_pox,
                        main_x_len + (fig_x - fig_x_len), main_y_len + (fig_y - fig_y_len))
                    self.vtk_widget.setGeometry(fig_x_pos, fig_y_pos, fig_x, fig_y)

    def _exportPNGImage(self, file_path):
        #x_pos, y_pos, x_len, y_len = self.vtk_widget.geometry().getRect()
        #self.vtk_widget.grab(QRect(0, 0, x_len, y_len)).save(file_path, "png")
        image_filter = vtk.vtkWindowToImageFilter()
        image_filter.SetInput(self.vtk_widget.GetRenderWindow())
        image_filter.Update()
        image_writer = vtk.vtkPNGWriter()
        image_writer.SetFileName(file_path)
        image_writer.SetInputConnection(image_filter.GetOutputPort())
        image_writer.Write()

    def exportImage(self):
        file_path, file_type = QFileDialog.getSaveFileName(self,      
            "Output Figure", "./", "PNG Image Files (*.png);;All Files (*)")
        if file_path != '':
            self._exportPNGImage(file_path)

    def show(self):
        self.vtk_widget.GetRenderWindow().GetInteractor().Initialize()
        super(VTKGraph, self).show()