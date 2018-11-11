# PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ImageSizeDialog import ImageSizeDialog

class MatplotGraph(QMainWindow):
    def __init__(self, parent = None):
        super(MatplotGraph, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Matplot Graph")
        screen_x_pos, screen_y_pos, screen_width, screen_height = QDesktopWidget().geometry().getRect()
        self.window_width = screen_width * 0.5
        self.window_height = screen_height * 0.5
        self.resize(self.window_width, self.window_height)
        self.move((screen_width - self.window_width) / 2,  (screen_height - self.window_height) / 2)
        # Note that this winodw should be modaless
        #self.setWindowModality(Qt.ApplicationModaless)
        # Destructed when closed
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Menu bar
        file_menu = self.menuBar().addMenu("File(&F)")
        resize_action = QAction("resize image", self)
        resize_action.triggered.connect(self.resizeImage)
        file_menu.addAction(resize_action)
        export_action = QAction("export image", self)
        export_action.triggered.connect(self.exportImage)
        file_menu.addAction(export_action)
        # Create the matplotlib widget
        self.plot_widget = FigureCanvas(Figure())
        self.setCentralWidget(self.plot_widget)
        self.plot_widget.setParent(self)
        # make the figure square
        cen_x_pos, cen_y_pos, cen_x_len, cen_y_len = self.centralWidget().geometry().getRect()
        ratio_tmp = (self.window_width - self.window_height) / (cen_x_len - cen_y_len)
        self.window_width -= (cen_x_len - cen_y_len) / 2 * ratio_tmp
        self.window_height += (cen_x_len - cen_y_len) / 2 * ratio_tmp
        self.resize(self.window_width, self.window_height)
        self.move((screen_width - self.window_width) / 2,  (screen_height - self.window_height) / 2)
        #FigureCanvas.setSizePolicy(self.plot_widget, QSizePolicy.Expanding, QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self.plot_widget)
        # Status Bar
        self.statusBar()

    def printMsg(self, msg_str):
        self.statusBar().showMessage(msg_str)

    def getPlotWidget(self):
        return self.plot_widget
    
    def show(self):
        self.plot_widget.draw()
        super(MatplotGraph, self).show()
    
    def resizeImage(self):
        main_x_pos, main_y_pox, main_x_len, main_y_len = self.geometry().getRect()
        fig_x_pos, fig_y_pos, fig_x_len, fig_y_len = self.plot_widget.geometry().getRect()
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
                    self.plot_widget.setGeometry(fig_x_pos, fig_y_pos, fig_x, fig_y)

    def exportImage(self):
        file_path, file_type = QFileDialog.getSaveFileName(self,      
            "Output Figure", "./", "PNG Image Files (*.png);;All Files (*)")
        if file_path != '':
            self.plot_widget.figure.savefig(file_path)
