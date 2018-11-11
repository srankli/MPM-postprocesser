import os
import sys
import time
import numpy as np
# HDF5 file operations
import h5py
# PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#from PyQt5.QtOpenGL import *
# Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt
# VTK
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from MatplotGraph import MatplotGraph
from AnimationGraph import AnimationGraph

class Mechanics1DDeformation(AnimationGraph):
    def __init__(self, particle_list, x_coord, parent = None, win_name = "Deformation - Mechanics 1D"):
        self.particle_list = particle_list
        self.x_coord = x_coord
        super(Mechanics1DDeformation, self).__init__(x_coord[:, 0], win_name, parent)

    def _createScene(self, frame_index):
        pcl_num = self.x_coord.shape[1] - 1
        points_coord = vtk.vtkPoints()
        for i in range(pcl_num):
            points_coord.InsertNextPoint(self.x_coord[frame_index][i+1], 0.0, 0.0)
        # gather all points
        points_cloud = vtk.vtkUnstructuredGrid()
        points_cloud.SetPoints(points_coord)
        #spheres at nodes
        ball = vtk.vtkSphereSource()
        ball.SetRadius(0.05) # need to choose????
        ball.SetThetaResolution(8)
        ball.SetPhiResolution(8)
        ball_glyph = vtk.vtkGlyph3D()
        ball_glyph.SetInputData(points_cloud)
        ball_glyph.SetSourceConnection(ball.GetOutputPort())
        # then the ball size is independent of Scalar
        ball_glyph.SetScaleModeToDataScalingOff()
        ball_mapper = vtk.vtkPolyDataMapper()
        ball_mapper.SetInputConnection(ball_glyph.GetOutputPort())
        ball_actor = vtk.vtkActor()
        ball_actor.SetMapper(ball_mapper)
        renderer = vtk.vtkRenderer()
        renderer.AddActor(ball_actor)
        renderer.SetBackground(0.0, 0.0, 0.0)
        vtk_win = self.vtk_widget.GetRenderWindow()
        vtk_win.AddRenderer(renderer)
        vtk_win.Render()

#####################################################################
class Mechanics2DDeformation(AnimationGraph):
    def __init__(self, particle_list, time_list, x_coord, y_coord, bg_mesh_x_coord, bg_mesh_y_coord, \
            parent = None, win_name = "Deformation - Mechanics 2D"):
        self.particle_list = particle_list
        self.particle_num = len(particle_list)
        self.time_list = time_list
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.bg_mesh_x_coord = bg_mesh_x_coord
        self.bg_mesh_y_coord = bg_mesh_y_coord
        super(Mechanics2DDeformation, self).__init__(time_list, win_name, parent)

    def _createScene(self, frame_index):
        points_coord = vtk.vtkPoints()
        #print(self.x_coord.shape)
        for i in range(self.particle_num):
            points_coord.InsertNextPoint(self.x_coord[frame_index][i], self.y_coord[frame_index][i], 0.0)
            #print(self.x_coord[frame_index][i])
            #print(self.y_coord[frame_index][i])
        # gather all points
        points_cloud = vtk.vtkUnstructuredGrid()
        points_cloud.SetPoints(points_coord)
        #spheres at nodes
        ball = vtk.vtkSphereSource()
        ball.SetRadius(0.05) # need to be chosen???
        ball.SetThetaResolution(8)
        ball.SetPhiResolution(8)
        ball_glyph = vtk.vtkGlyph3D()
        ball_glyph.SetInputData(points_cloud)
        ball_glyph.SetSourceConnection(ball.GetOutputPort())
        # then the ball size is independent of Scalar
        ball_glyph.SetScaleModeToDataScalingOff()
        ball_mapper = vtk.vtkPolyDataMapper()
        ball_mapper.SetInputConnection(ball_glyph.GetOutputPort())
        # Draw background mesh
        bg_mesh_mapper = None
        # check if background mesh is valid
        if self.bg_mesh_x_coord and self.bg_mesh_y_coord and \
            len(self.bg_mesh_x_coord) > 1 and len(self.bg_mesh_y_coord) > 1:
            x_min = self.bg_mesh_x_coord[0]
            x_max = self.bg_mesh_x_coord[-1]
            y_min = self.bg_mesh_y_coord[0]
            y_max = self.bg_mesh_y_coord[-1]
            bg_mesh_points = vtk.vtkPoints()
            bg_mesh_lines = vtk.vtkCellArray()
            # Horizontal lines
            for i in range(len(self.bg_mesh_y_coord)):
                bg_mesh_points.InsertPoint(2*i,   x_min, self.bg_mesh_y_coord[i], 0.0)
                bg_mesh_points.InsertPoint(2*i+1, x_max, self.bg_mesh_y_coord[i], 0.0)
                bg_mesh_lines.InsertNextCell(2)
                bg_mesh_lines.InsertCellPoint(2*i)
                bg_mesh_lines.InsertCellPoint(2*i+1)
            # Vertical lines
            cur_index = len(self.bg_mesh_y_coord)*2
            for i in range(len(self.bg_mesh_x_coord)):
                bg_mesh_points.InsertPoint(cur_index+2*i,   self.bg_mesh_x_coord[i], y_min, 0.0)
                bg_mesh_points.InsertPoint(cur_index+2*i+1, self.bg_mesh_x_coord[i], y_max, 0.0)
                bg_mesh_lines.InsertNextCell(2)
                bg_mesh_lines.InsertCellPoint(cur_index+2*i)
                bg_mesh_lines.InsertCellPoint(cur_index+2*i+1)
            mesh_lines_data = vtk.vtkPolyData()
            mesh_lines_data.SetPoints(bg_mesh_points)
            mesh_lines_data.SetLines(bg_mesh_lines)
            bg_mesh_mapper = vtk.vtkPolyDataMapper()
            bg_mesh_mapper.SetInputData(mesh_lines_data)
        # Create scene
        ball_actor = vtk.vtkActor()
        ball_actor.SetMapper(ball_mapper)
        renderer = vtk.vtkRenderer()
        renderer.AddActor(ball_actor)
        if bg_mesh_mapper:
            bg_mesh_actor = vtk.vtkActor()
            bg_mesh_actor.SetMapper(bg_mesh_mapper)
            renderer.AddActor(bg_mesh_actor)
        renderer.SetBackground(0.0, 0.0, 0.0)
        vtk_win = self.getRenderWindow()
        vtk_win.AddRenderer(renderer)
        vtk_win.Render()

#################################################################
class AttrWidget(QWidget):
    def __init__(self, parent = None):
        super(AttrWidget, self).__init__(parent)
        attr_widget_layout = QGridLayout()
        self.setLayout(attr_widget_layout)
        attr_widget_layout.setColumnStretch(0, 5)
        attr_widget_layout.setColumnStretch(1, 2)
        attr_widget_layout.setRowStretch(0, 1)
        attr_widget_layout.setRowStretch(1, 20)
        # label for attribute name
        self.attr_name_label = QLabel(self)
        self.attr_name_label.setText("Attributes")
        attr_widget_layout.addWidget(self.attr_name_label, 0, 0)
        # attribute table
        self.attr_table = QTableWidget(self)
        self.attr_table.setRowCount(0)
        self.attr_table.setColumnCount(2)
        self.attr_table.setHorizontalHeaderLabels(["Name", "Value"])
        # set the table read only
        self.attr_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # hide row number
        self.attr_table.verticalHeader().hide()
        self.attr_table_last_row = 0
        attr_widget_layout.addWidget(self.attr_table, 1, 0)
        # label for attribute list
        self.attr_list_name = QLabel(self)
        attr_widget_layout.addWidget(self.attr_list_name, 0, 1)
        # attribute list
        self.attr_list = QListWidget(self)
        attr_widget_layout.addWidget(self.attr_list, 1, 1)
        self.attr_index_pairs = []

    def setAttrName(self, name):
        self.attr_name_label.setText(name)

    def setAttrListName(self, name):
        self.attr_list_name.setText(name)

    def addAttr(self, attr_key, attr_value):
        self.attr_table.insertRow(self.attr_table_last_row)
        self.attr_table.setItem(self.attr_table_last_row, 0, QTableWidgetItem(attr_key))
        self.attr_table.setItem(self.attr_table_last_row, 1, QTableWidgetItem(attr_value))
        self.attr_table_last_row += 1

    def addAttrList(self, attr_index_list):
        #print(len(attr_index_list))
        self.attr_index_pairs.clear()
        if (len(attr_index_list)):
            i = 0
            for index in attr_index_list:
                self.attr_index_pairs.append((index, i))
                i += 1
            self.attr_index_pairs.sort(key = lambda x:x[0])
            #print(type(attr_index_list[0]))
            if type(attr_index_list[0]) == np.uint64:
                for pair in self.attr_index_pairs:
                    self.attr_list.addItem(str(pair[0]))
            elif type(attr_index_list[0]) == np.float64:
                # may need to format the float number in the future.
                for pair in self.attr_index_pairs:
                    self.attr_list.addItem(str(pair[0]))

    def clear(self):
        #self.attr_name_label.setText('')
        self.attr_table.clear()
        self.attr_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.attr_table.setRowCount(0)
        self.attr_table_last_row = 0
        self.attr_list.clear()
        self.attr_list_name.setText("")

class MainWindow(QMainWindow):
    """ Use to display MPM calculation result stored in hdf5 file """
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        # Initialize variables 
        self.file_dir = ""
        self.file_name = ""
        self.res_file = None
        self.child_wins = None
        # vtk widget
        self.iren = None
        # Initialize window
        self.setWindowTitle("MPM Results")
        screen_size = QDesktopWidget().geometry()
        self.window_width = screen_size.width() * 0.6
        self.window_height = screen_size.height() * 0.8
        self.resize(self.window_width, self.window_height)
        self.move((screen_size.width() - self.window_width) / 2,  (screen_size.height() - self.window_height) / 2)
        # Initialize menu bar
        file_menu = self.menuBar().addMenu("F&ile")
        open_file_action = self._create_action("Open", "Ctrl+O", None, "Open hdf5 file.")
        open_file_action.triggered.connect(self.openFile)
        close_file_action = self._create_action("Close", "Ctrl+C", None, "Close hdf5 file.")
        close_file_action.triggered.connect(self.closeFile)
        self._add_actions_to_menu(file_menu, (open_file_action, close_file_action))
        graphics_menu = self.menuBar().addMenu("G&raphics")
        time_curve_action = self._create_action("Time Curve", None, None, "Create time curve.")
        time_curve_action.triggered.connect(self.createTimeCurve)
        field_animation_action = self._create_action("Display Deformation", None, None, "Display deformation.")
        field_animation_action.triggered.connect(self.displayDeformation) 
        self._add_actions_to_menu(graphics_menu, (time_curve_action, field_animation_action))
        # Initialize window layout
        main_splitter = QSplitter(self)
        main_splitter.setOrientation(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        # Frame for content structure of hdf5 file
        left_frame = QFrame(main_splitter)
        main_splitter.setStretchFactor(0, 3)
        main_splitter.addWidget(left_frame)
        left_frame_layout = QVBoxLayout()
        left_frame.setLayout(left_frame_layout)
        # Tree widget
        self.file_content_tree = QTreeWidget(left_frame)
        left_frame_layout.addWidget(self.file_content_tree)
        self.file_content_tree.setColumnCount(2)
        self.file_content_tree.setHeaderLabels(['Name', 'Type'])
        root = QTreeWidgetItem(self.file_content_tree)
        root.setText(0, "null")
        self.file_content_tree.addTopLevelItem(root)
        #self.file_content_tree.itemDoubleClicked.connect(self.showAttrOfSelectedItem)
        self.file_content_tree.itemClicked.connect(self.showAttrOfSelectedItem)
        # Frame for displaying attribute of group or dataset
        right_frame = QFrame(main_splitter)
        main_splitter.setStretchFactor(1, 5)
        main_splitter.addWidget(right_frame)
        right_frame_layout = QVBoxLayout()
        right_frame.setLayout(right_frame_layout)
        right_splitter = QSplitter(right_frame)
        right_splitter.setOrientation(Qt.Vertical)
        right_frame_layout.addWidget(right_splitter)
        # attributes
        self.attr_widget = AttrWidget(right_frame)       
        right_splitter.setStretchFactor(0, 5)
        right_splitter.addWidget(self.attr_widget)
        # message box
        self.message_box = QTextEdit(right_frame)
        self.message_box.setReadOnly(True)
        right_splitter.setStretchFactor(1, 2)
        right_splitter.addWidget(self.message_box)
        # Status Bar
        self.statusBar()
        # first try to open file
        self.openFile()

    def _create_action(self, text, shortcut=None, icon=None, tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if checkable:
            action.setCheckable(True)
        return action

    def _add_actions_to_menu(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def printMsg(self, msg):
        self.message_box.insertPlainText(msg + "\n")

    def printError(self, error_msg):
        self.printMsg("Error: " + error_msg)

    def printWarning(self, warning_msg):
        self.printMsg("Warning: " + warning_msg)

    def _addChild(self, file_node, tree_node):
        if hasattr(file_node, "keys") and len(file_node.keys()):
            # if file node has child node
            for child_node_name in file_node.keys():
                tree_child_node = QTreeWidgetItem(tree_node)
                tree_child_node.setText(0, child_node_name)
                child_file_node = file_node[child_node_name]
                child_file_node_attr_key = child_file_node.attrs.keys()
                if type(child_file_node) == h5py._hl.group.Group:
                    if 'OutputIndex' in child_file_node_attr_key:
                        tree_child_node.setText(1, "Output")
                    elif 'ObjectIndex' in child_file_node_attr_key:
                        tree_child_node.setText(1, "Object")
                    elif "BackgroundMesh" == child_node_name:
                        tree_child_node.setText(1, "BgMesh")
                elif type(file_node[child_node_name]) == h5py._hl.dataset.Dataset:
                    if 'XCoord' == child_node_name or \
                        'YCoord' == child_node_name or \
                        'ZCoord' == child_node_name:
                        tree_child_node.setText(1, "MeshCoord")
                    elif 'Time' == child_node_name:
                        tree_child_node.setText(1, "Time")
                    elif 'IterationIndex' == child_node_name:
                        tree_child_node.setText(1, "IterationIndex")
                    elif 'ParticleIndex' == child_node_name:
                        tree_child_node.setText(1, "Particle")
                    else:
                        tree_child_node.setText(1, "Field")
                tree_node.addChild(tree_child_node)
                self._addChild(file_node[child_node_name], tree_child_node)

    def openFile(self):
        # Open hdf5 file
        file_path, file_type = QFileDialog.getOpenFileName(self,
            "Select result file", "./", "HDF Files (*.h5);;All Files (*)")
        if (file_path != ''):
            file_dir_tmp, file_name_tmp = os.path.split(file_path)
            try:
                file_tmp = h5py.File(file_path, 'r')
            except OSError:
                QMessageBox.warning(self, "Error", "Failed to read file %s." % file_name_tmp, QMessageBox.Cancel)
            else:
                self.file_dir = file_dir_tmp
                self.file_name = file_name_tmp
                # close old file.
                if self.res_file:
                    self.res_file.close()
                self.res_file = file_tmp
                self.setWindowTitle("%s - Results Visualization" % self.file_name)
                # Show hdf5 file content
                self.file_content_tree.clear()
                root = QTreeWidgetItem(self.file_content_tree)
                root.setText(0, self.file_name)
                root.setText(1, "File")
                self.file_content_tree.addTopLevelItem(root)
                self._addChild(self.res_file, root)
                # Clear attributes widget
                self.attr_widget.clear()

    def closeFile(self):
        self.file_dir = ""
        self.file_name = ""
        self.child_wins = None
        # vtk widget
        self.iren = None
        self.file_content_tree.clear()
        self.attr_widget.clear()
        if self.res_file:
            self.res_file.close()
            self.res_file = None

    def closeEvent(self, e):
        if self.res_file:
            self.res_file.close()

    def _getObject(self, item):
        item_name = item.text(0)
        parent = item.parent()
        if parent:
            return self._getObject(parent)[item_name]
        else:
            return self.res_file

    def showAttrOfSelectedItem(self):
        def code_list_to_string(code_list):
            char_list = []
            for char_code in code_list:
                    char_list.append(chr(char_code))
            return "".join(char_list)
        # Simulation Type:
        # 0. Invalid Simulation
        # 1. Mechanics 1D
	    # 2. Hydromechanics 1D
	    # 3. Mechanics 2D
	    # 4. Hydromechanics 2D
        self.attr_widget.clear()
        cur_item = self.file_content_tree.currentItem()
        item_name = cur_item.text(0)
        item_type = cur_item.text(1)
        if item_type == "Output":
            # add attributes
            cur_item_obj = self._getObject(cur_item)
            cur_item_attrs = cur_item_obj.attrs
            cur_item_attr_keys = cur_item_attrs.keys()
            if "OutputIndex" in cur_item_attr_keys:
                self.attr_widget.addAttr("Output Index", str(cur_item_attrs["OutputIndex"]))
            if 'OutputName' in cur_item_attr_keys:
                self.attr_widget.addAttr("Output Name", code_list_to_string(cur_item_attrs['OutputName']))
            if "TimeNumber" in cur_item_attr_keys:
                self.attr_widget.addAttr("Time Number", str(cur_item_attrs["TimeNumber"]))
            if "ObjectNumber" in cur_item_attr_keys:
                self.attr_widget.addAttr("Object Number", str(cur_item_attrs["ObjectNumber"]))
            # add time list
            self.attr_widget.setAttrListName("Time")
            if "Time" in cur_item_obj.keys():
                time_num = len(cur_item_obj["Time"])
                #print(pcl_num)
                if time_num > 200:
                    time_num = 200
                self.attr_widget.addAttrList(cur_item_obj["Time"][0:time_num])
        elif item_type == "Object":
            # add attributes
            cur_item_obj = self._getObject(cur_item)
            cur_item_attrs = cur_item_obj.attrs
            cur_item_attr_keys = cur_item_attrs.keys()
            if "ObjectIndex" in cur_item_attr_keys:
                self.attr_widget.addAttr("Object Index", str(cur_item_attrs["ObjectIndex"]))
            if 'ObjectName' in cur_item_attr_keys:
                self.attr_widget.addAttr("Object Name", code_list_to_string(cur_item_attrs['ObjectName']))
            if "SimulationType" in cur_item_attr_keys:
                self.attr_widget.addAttr("Simulation Type", str(cur_item_attrs["SimulationType"]))
            if "SimulationTypeName" in cur_item_attr_keys:
                self.attr_widget.addAttr("Simulation Type Name", code_list_to_string(cur_item_attrs['SimulationTypeName']))
            if "FieldNumber" in cur_item_attr_keys:
                self.attr_widget.addAttr("Field Number", str(cur_item_attrs["FieldNumber"]))
            if "ParticleNumber" in cur_item_attr_keys:
                self.attr_widget.addAttr("Particle Number", str(cur_item_attrs["ParticleNumber"]))
            # add particle index list
            self.attr_widget.setAttrListName("Particle index")
            if "ParticleIndex" in cur_item_obj.keys():
                pcl_num = len(cur_item_obj["ParticleIndex"])
                #print(pcl_num)
                if pcl_num > 100:
                    pcl_num = 100
                self.attr_widget.addAttrList(cur_item_obj["ParticleIndex"][0:pcl_num])
        elif item_type == "Field":
            cur_item_obj = self._getObject(cur_item)
            cur_item_attrs = cur_item_obj.attrs
            cur_item_attr_keys = cur_item_attrs.keys()
            if "FieldType" in cur_item_attr_keys:
                self.attr_widget.addAttr("Field Type", str(cur_item_attrs["FieldType"]))
            if "FieldName" in cur_item_attr_keys:
                self.attr_widget.addAttr("Field Name", code_list_to_string(cur_item_attrs["FieldName"]))
            # add particle index list
            self.attr_widget.setAttrListName("Particle index")
            parent_item = cur_item.parent()
            parent_item_obj = self._getObject(parent_item)
            parent_item_attrs = parent_item_obj.attrs
            parent_item_attr_keys = parent_item_obj.attrs.keys()
            if "ParticleNumber" in parent_item_attr_keys:
                self.attr_widget.addAttr("Particle Number", str(parent_item_attrs["ParticleNumber"]))
            if "ParticleIndex" in parent_item_obj.keys():
                pcl_num = len(parent_item_obj["ParticleIndex"])
                #print(pcl_num)
                if pcl_num > 100:
                    pcl_num = 100
                self.attr_widget.addAttrList(parent_item_obj["ParticleIndex"][0:pcl_num])

    def createTimeCurve(self):
        cur_item = self.file_content_tree.currentItem()
        cur_obj = self._getObject(cur_item)
        if cur_item.text(1) != "Field":
            self.printError("Need to select a field dataset.")
            return
        cur_row = self.attr_widget.attr_list.currentRow()
        if cur_row < 0:
            # no particle index is selected from the qlistwidget
            self.printError("Need to select a particle index.")
            return
        cur_pcl_output_pos = self.attr_widget.attr_index_pairs[cur_row][1]
        # create new window
        self.child_win = MatplotGraph(self)
        child_win = self.child_win
        plot_widget = child_win.getPlotWidget()
        data_subplot = plot_widget.figure.add_subplot(111)
        # data and time
        data = cur_obj[:, cur_pcl_output_pos]
        grandparent_item = cur_item.parent().parent() # output group
        grandparent_obj = self._getObject(grandparent_item)
        data_time = grandparent_obj["Time"]
        # plot graph
        data_subplot.plot(data_time, data, 'k-')
        data_subplot.set_title(cur_item.text(0) + ' - time relation')
        #data_subplot.set_xlim([0, 5])
        data_subplot.set_xlabel('Time')
        data_subplot.set_ylabel(cur_item.text(0))
        child_win.show()

    # currently only display one object
    def displayDeformation(self):
        cur_item = self.file_content_tree.currentItem()
        cur_obj = self._getObject(cur_item)
        if cur_item.text(1) != "Object":
            self.printError("Need to select an object.")
            return
        if "ParticleIndex" not in cur_obj.keys():
            self.printError("Selected object has no information of particle index.")
            return
        if 'SimulationType' not in cur_obj.attrs.keys():
            self.printError("Selected object has no attribute of simulaiton type.")
            return
        sim_type = cur_obj.attrs['SimulationType']
        if sim_type == 1: # 1D mechanics
            if "x" not in cur_obj.keys():
                self.printError("Selected object has no output of x coordinates.")
                return
            parent_item = cur_item.parent() # output group
            parent_obj = self._getObject(parent_item)
            self.child_win = Mechanics1DDeformation(cur_obj["ParticleIndex"],\
                                            parent_obj["Time"], cur_obj["x"], self)
            self.child_win.show()
        elif sim_type == 3: # 2D mechanics
            if "x" not in cur_obj.keys():
                self.printError("Selected object has no output of x coordinates.")
                return
            if "y" not in cur_obj.keys():
                self.printError("Selected object has no output of y coordinates.")
                return
            # Get time: parent_obj is used to get time
            parent_item = cur_item.parent() # output group
            parent_obj = self._getObject(parent_item)
            # Get mesh: 
            bg_mesh_x_coord = None
            bg_mesh_y_coord = None
            if "BackgroundMesh" in self.res_file.keys():
                bg_mesh = self.res_file["BackgroundMesh"]
                if "XCoord" in bg_mesh.keys() and "YCoord" in bg_mesh.keys():
                    bg_mesh_x_coord = bg_mesh["XCoord"]
                    bg_mesh_y_coord = bg_mesh["YCoord"]
            # Create window
            # for i in range(len(parent_obj["Time"])):
            #     print(parent_obj["Time"][i])
            self.child_win = \
                Mechanics2DDeformation(cur_obj["ParticleIndex"], parent_obj["Time"], \
                    cur_obj["x"], cur_obj["y"], bg_mesh_x_coord, bg_mesh_y_coord, self)
            self.child_win.show()

    # def CreateRender(self):
    #     source = vtk.vtkSphereSource()
    #     source.SetCenter(0.0, 0.0, 0.0)
    #     source.SetRadius(5.0)
    #     mapper = vtk.vtkPolyDataMapper()
    #     mapper.SetInputConnection(source.GetOutputPort())
    #     actor = vtk.vtkActor()
    #     actor.SetMapper(mapper)
    #     ren = vtk.vtkRenderer()
    #     ren.AddActor(actor)
    #     ren.ResetCamera()
    #     return ren

    # Remove all widget from layout
    # def _remove_widget_from_layout(self, layout): 
    #     for i in reversed(range(layout.count())): 
    #         widgetToRemove = layout.itemAt(i).widget()
    #         # remove it from the layout list
    #         layout.removeWidget(widgetToRemove)
    #         # remove it from the gui
    #         widgetToRemove.setParent(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()