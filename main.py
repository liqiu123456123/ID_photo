import copy
import cv2
import sys
import numpy as np
import math
from image_label import ImageLabel
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QMainWindow, QMenu, QAction
from PyQt5.QtCore import Qt, QSize
from PyQt5.Qt import QToolButton
from scipy import ndimage


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.btn_cancel = None
        self.btn_confirm = None
        self.control_layout = None
        self.control = None
        self.btn_undo = None
        self.btn_save = None
        self.btn_open = None
        self.title_button_layout = None
        self.operation = None
        self.title_layout = None
        self.title = None
        self.central_widget_layout = None
        self.central_widget = None
        self.last_img = None
        self.current_operation = None
        self.original_img = None
        self.icon_path = None
        self.current_img = None
        self.setupUi()

    def setupUi(self):

        self.resize(926, 806)
        # self.central_widget:主窗口
        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget_layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.central_widget_layout)
        # 主窗口布局间隙
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget_layout.setSpacing(0)
        #  self.title:横向菜单栏
        self.title = QtWidgets.QFrame(self.central_widget)
        self.title.setMinimumSize(QtCore.QSize(0, 55))
        self.title.setMaximumSize(QtCore.QSize(188888, 55))
        self.title.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.title.setFrameShadow(QtWidgets.QFrame.Raised)
        # self.title_layout：横向菜单栏布局
        self.title_layout = QtWidgets.QHBoxLayout()
        self.title.setLayout(self.title_layout)
        self.operation = QtWidgets.QFrame(self.title)
        self.operation.setMinimumSize(QtCore.QSize(250, 45))
        self.operation.setMaximumSize(QtCore.QSize(250, 45))
        self.operation.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.operation.setFrameShadow(QtWidgets.QFrame.Raised)
        # title_button_layout:title的按钮横向布局
        self.title_button_layout = QtWidgets.QHBoxLayout()
        self.operation.setLayout(self.title_button_layout)
        self.btn_open = QtWidgets.QToolButton(self.operation)
        self.title_button_layout.addWidget(self.btn_open)
        self.btn_save = QtWidgets.QToolButton(self.operation)
        self.title_button_layout.addWidget(self.btn_save)
        self.btn_undo = QtWidgets.QToolButton(self.operation)
        self.title_button_layout.addWidget(self.btn_undo)
        self.title_layout.addWidget(self.operation)
        # spacerItem弹簧
        spacerItem = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.title_layout.addItem(spacerItem)
        # self.control:确定取消按钮控件
        self.control = QtWidgets.QFrame(self.title)
        self.control.setMinimumSize(QtCore.QSize(0, 45))
        self.control.setMaximumSize(QtCore.QSize(120, 45))
        self.control.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.control.setFrameShadow(QtWidgets.QFrame.Raised)
        self.control_layout = QtWidgets.QHBoxLayout(self.control)
        self.btn_confirm = QtWidgets.QToolButton(self.control)
        self.control_layout.addWidget(self.btn_confirm)
        self.btn_cancel = QtWidgets.QToolButton(self.control)
        self.control_layout.addWidget(self.btn_cancel)
        self.title_layout.addWidget(self.control)
        # 主窗口布局添加标题菜单控件
        self.central_widget_layout.addWidget(self.title)
        self.action_img_layout = QtWidgets.QHBoxLayout()
        self.action_img_layout.setSpacing(0)
        self.action_back_frame = QtWidgets.QFrame(self.central_widget)
        self.action_back_frame.setMinimumSize(QtCore.QSize(100, 0))
        self.action_back_frame.setMaximumSize(QtCore.QSize(100, 16777215))
        self.action_back_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.action_back_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.action_options_frame = QtWidgets.QFrame(self.action_back_frame)
        self.action_options_frame.setGeometry(QtCore.QRect(10, 0, 56, 500))
        self.action_options_frame.setMinimumSize(QtCore.QSize(0, 500))
        self.action_options_frame.setMaximumSize(QtCore.QSize(16777215, 500))
        self.action_options_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.action_options_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        # 图片操作选项竖向布局
        self.action_layout = QtWidgets.QVBoxLayout(self.action_options_frame)
        self.btn_clip = QtWidgets.QToolButton(self.action_options_frame)
        self.btn_clip.setMinimumSize(QtCore.QSize(50, 0))
        self.action_layout.addWidget(self.btn_clip)
        self.btn_correction = QtWidgets.QToolButton(self.action_options_frame)
        self.btn_correction.setMinimumSize(QtCore.QSize(50, 0))
        self.action_layout.addWidget(self.btn_correction, 0, QtCore.Qt.AlignLeft)
        self.btn_flip = QtWidgets.QToolButton(self.action_options_frame)
        self.btn_flip.setMinimumSize(QtCore.QSize(50, 0))
        self.action_layout.addWidget(self.btn_flip)
        flip_menu = QMenu()
        action_horizontal_flip = QAction("垂直翻转", flip_menu)
        action_vertical_flip = QAction("水平翻转", flip_menu)
        action_diagonal_flip = QAction("180度翻转", flip_menu)
        flip_menu.addAction(action_horizontal_flip)
        flip_menu.addAction(action_vertical_flip)
        flip_menu.addAction(action_diagonal_flip)
        action_horizontal_flip.triggered.connect(self.horizontal_flip_img)
        action_vertical_flip.triggered.connect(self.vertical_flip_img)
        action_diagonal_flip.triggered.connect(self.diagonal_flip_img)
        self.btn_flip.setMenu(flip_menu)
        self.btn_flip.setPopupMode(QToolButton.MenuButtonPopup)
        self.btn_base_color = QtWidgets.QToolButton(self.action_options_frame)
        base_color_menu = QMenu()
        action_blue_to_red = QAction(QIcon("红底.png"), "蓝底转红底", base_color_menu)
        action_blue_to_white = QAction(QIcon("白底.png"), "蓝底转白底", base_color_menu)
        action_white_to_red = QAction(QIcon("红底.png"), "白底转红底", base_color_menu)
        action_white_to_blue = QAction(QIcon("蓝底.png"), "白底转蓝底", base_color_menu)
        action_red_to_blue = QAction(QIcon("蓝底.png"), "红底转蓝底", base_color_menu)
        action_red_to_white = QAction(QIcon("白底.png"), "红底转白底", base_color_menu)
        base_color_menu.addAction(action_blue_to_red)
        base_color_menu.addAction(action_blue_to_white)
        base_color_menu.addAction(action_white_to_red)
        base_color_menu.addAction(action_white_to_blue)
        base_color_menu.addAction(action_red_to_blue)
        base_color_menu.addAction(action_red_to_white)
        self.btn_base_color.setMenu(base_color_menu)
        self.btn_base_color.setPopupMode(QToolButton.MenuButtonPopup)
        action_blue_to_red.triggered.connect(self.base_color_img_blue_to_red)
        action_blue_to_white.triggered.connect(self.base_color_img_blue_to_white)
        action_red_to_blue.triggered.connect(self.base_color_img_red_to_blue)
        action_red_to_white.triggered.connect(self.base_color_img_red_to_white)
        self.btn_base_color.setMinimumSize(QtCore.QSize(50, 0))
        self.action_layout.addWidget(self.btn_base_color)
        self.btn_size = QtWidgets.QToolButton(self.action_options_frame)
        self.btn_size.setMinimumSize(QtCore.QSize(50, 0))
        self.action_layout.addWidget(self.btn_size)
        size_menu = QMenu()
        action_one_size = QAction("一寸照", size_menu)
        action_two_size = QAction("二寸照", size_menu)
        size_menu.addAction(action_one_size)
        size_menu.addAction(action_two_size)
        action_one_size.triggered.connect(self.size_one_img)
        action_two_size.triggered.connect(self.size_two_img)
        self.btn_size.setMenu(size_menu)
        self.btn_size.setPopupMode(QToolButton.MenuButtonPopup)

        self.action_img_layout.addWidget(self.action_back_frame)
        self.img_frame = QtWidgets.QFrame(self.central_widget)
        self.img_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.img_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        # self.img_frame布局
        self.img_frame_layout = QtWidgets.QHBoxLayout()
        self.img_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.img_frame_layout.setSpacing(0)
        self.img_frame.setLayout(self.img_frame_layout)
        self.img_display = ImageLabel(self.img_frame)
        self.img_frame_layout.addWidget(self.img_display)
        self.action_img_layout.addWidget(self.img_frame)
        self.central_widget_layout.addLayout(self.action_img_layout)
        self.setCentralWidget(self.central_widget)
        self.control.hide()
        # 按钮显示文字
        self.btn_open.setText("打开")
        self.btn_open.setIcon(QIcon("./icon/open.png"))
        self.btn_open.setIconSize(QSize(36, 36))
        self.btn_open.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_save.setText("保存")
        self.btn_save.setIcon(QIcon("./icon/save.png"))
        self.btn_save.setIconSize(QSize(36, 36))
        self.btn_save.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_undo.setText("恢复")
        self.btn_undo.setIcon(QIcon("./icon/undo.png"))
        self.btn_undo.setIconSize(QSize(36, 36))
        self.btn_undo.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_confirm.setText("确定")
        self.btn_cancel.setText("取消")
        self.btn_clip.setText("裁剪")
        self.btn_clip.setIcon(QIcon("./icon/clip.png"))
        self.btn_clip.setIconSize(QSize(36, 36))
        self.btn_clip.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_correction.setText("矫正")
        self.btn_correction.setIcon(QIcon("./icon/correction.png"))
        self.btn_correction.setIconSize(QSize(36, 36))
        self.btn_correction.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_flip.setText("翻转")
        self.btn_flip.setIcon(QIcon("./icon/flip.png"))
        self.btn_flip.setIconSize(QSize(36, 36))
        self.btn_flip.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_base_color.setText("换底")
        self.btn_base_color.setIcon(QIcon("./icon/base_color.png"))
        self.btn_base_color.setIconSize(QSize(36, 36))
        self.btn_base_color.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.btn_size.setText("尺寸")
        self.btn_size.setIcon(QIcon("./icon/size.png"))
        self.btn_size.setIconSize(QSize(36, 36))
        self.btn_size.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # 按钮绑定事件
        self.btn_open.clicked.connect(self.open_img)
        self.btn_save.clicked.connect(self.save_img)
        self.btn_undo.clicked.connect(self.undo_img)
        self.btn_confirm.clicked.connect(self.confirm_img)
        self.btn_cancel.clicked.connect(self.cancel_img)
        self.btn_clip.clicked.connect(self.clip_img)
        self.btn_correction.clicked.connect(self.correction_img)

        # 对象名
        self.setObjectName("MainWindow")
        self.central_widget.setObjectName("central_widget")
        self.central_widget_layout.setObjectName("central_widget_layout")
        self.title_layout.setObjectName("title_layout")
        self.title.setObjectName("title")
        self.operation.setObjectName("operation")
        self.title_button_layout.setObjectName("title_button_layout")
        self.btn_open.setObjectName("btn_open")
        self.btn_save.setObjectName("btn_save")
        self.btn_undo.setObjectName("btn_undo")
        self.control.setObjectName("control")
        self.control_layout.setObjectName("control_layout")
        self.btn_confirm.setObjectName("btn_confirm")
        self.btn_cancel.setObjectName("btn_cancel")
        self.action_img_layout.setObjectName("action_img_layout")
        self.action_back_frame.setObjectName("action_back_frame")
        self.action_options_frame.setObjectName("action_options_frame")
        self.action_layout.setObjectName("action_layout")
        self.btn_clip.setObjectName("btn_clip")
        self.btn_correction.setObjectName("btn_correction")
        self.btn_flip.setObjectName("btn_flip")
        self.btn_base_color.setObjectName("btn_base_color")
        self.btn_size.setObjectName("btn_size")
        self.img_frame.setObjectName("img_frame")
        self.img_frame_layout.setObjectName("img_frame_layout")
        self.img_display.setObjectName("img_display")

        # 字体统一定义
        font = QtGui.QFont()
        font.setPointSize(8)
        self.setFont(font)
        self.btn_open.setFont(font)
        self.btn_save.setFont(font)
        self.btn_base_color.setFont(font)
        self.btn_size.setFont(font)
        self.btn_flip.setFont(font)
        self.btn_correction.setFont(font)
        self.btn_clip.setFont(font)
        self.btn_cancel.setFont(font)
        self.btn_confirm.setFont(font)
        self.btn_undo.setFont(font)

        # 格式设置
        # 定义公共的样式字符串
        transparent_button_style = "background: rgba(0, 0, 0, 0); color: rgb(255, 255, 255);"
        gray_button_style = "background: rgb(80, 80, 80); color: rgb(255, 255, 255);"

        # 设置中央窗口的样式
        self.central_widget.setStyleSheet("background: rgb(252, 255, 255);")

        # 设置标题的样式
        self.title.setStyleSheet("background: rgb(60, 60, 60);")

        # 设置按钮的样式（重用透明按钮样式）
        buttons = [self.btn_open, self.btn_save, self.btn_undo, self.btn_confirm, self.btn_cancel,
                   self.btn_clip, self.btn_correction, self.btn_flip, self.btn_base_color, self.btn_size]
        for btn in buttons:
            btn.setStyleSheet(transparent_button_style)

            # 设置特定按钮的样式（如果它们有不同于其他按钮的样式）
        self.action_back_frame.setStyleSheet(gray_button_style)

    def open_img(self):
        """
        “打开” 按钮的点击事件
        """
        img_name, img_type = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;*.png;*.jpeg")
        if (img_name == "") or (img_name is None):
            self.__show_warning_message_box("未选择图片")
            return

        img = cv2.imread(img_name)  # 读取图像
        self.showImage(img)
        self.current_img = img
        self.last_img = self.current_img
        self.original_img = copy.deepcopy(self.current_img)
        self.original_img_path = img_name

    def showImage(self, img, is_grayscale=False):
        x = img.shape[1]  # 获取图像大小
        y = img.shape[0]
        self.zoomscale = 1  # 图片放缩尺度
        bytesPerLine = 3 * x
        if len(img.shape) == 2:  # 判断是否为灰度图，如果是灰度图，需要转换成三通道图
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        frame = QImage(img.data, x, y, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pix = QPixmap.fromImage(frame)
        self.img_display.setPixmap(pix)
        self.img_display.repaint()

    def clip_img(self):
        """
        "裁剪"按钮事件
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return

        self.current_operation = "clip"
        self.img_display.flag = True  # 标记 img_panel 可以绘制矩形，从而选择裁剪区域
        self.img_display.setCursor(Qt.CrossCursor)
        self.control.show()

    def crop_image(self, src_img, x_start, x_end, y_start, y_end):
        """
        :param src_img: 原始图片
        :param x_start: x 起始坐标
        :param x_end:  x 结束坐标
        :param y_start:  y 开始坐标
        :param y_end: y 结束坐标
        :return:
        """
        tmp_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2RGB)
        tmp_img = tmp_img[y_start:y_end, x_start:x_end]  # 长，宽
        return cv2.cvtColor(tmp_img, cv2.COLOR_RGB2BGR)

    def __show_warning_message_box(self, msg):
        QMessageBox.warning(self, "警告", msg, QMessageBox.Ok)

    def __show_info_message_box(self, msg):
        QMessageBox.information(self, "提示", msg, QMessageBox.Ok)

    def undo_img(self):
        """
        “恢复” 按钮的点击事件，将图片恢复到最初的状态
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        self.current_img = self.original_img
        self.last_img = self.current_img
        self.showImage(self.current_img)

    def save_img(self):
        """
         “保存” 按钮的点击事件，将图片恢复到最初的状态
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return

        ext_name = self.original_img_path[self.original_img_path.rindex("."):]
        img_path, img_type = QFileDialog.getSaveFileName(self, "保存图片", self.original_img_path, "*" + ext_name)
        cv2.imwrite(img_path, self.current_img)

    def confirm_img(self):
        """
        "确定"按钮时间
        :return:
        """
        self.control.hide()
        # 根据操作类型进行相应的处理
        if self.current_operation == "clip":
            x_start, x_end = self.img_display.img_x_start, self.img_display.img_x_end
            y_start, y_end = self.img_display.img_y_start, self.img_display.img_y_end
            self.current_img = self.crop_image(self.current_img, x_start, x_end, y_start, y_end)
            self.showImage(self.current_img)
            self.img_display.clearRect()
            self.img_display.flag = False  # 标记 img_display 不能绘制矩形，从而禁止选择裁剪区域
        elif self.current_operation == "base_color":
            self.last_img = self.current_img
        elif self.current_operation == "flip":
            self.last_img = self.current_img
        elif self.current_operation == "size":
            self.last_img = self.current_img
        elif self.current_operation == "correction":
            self.last_img = self.current_img
        self.last_img = self.current_img  # 将当前操作得到的图片结果保存到 last_img 中（相对于后面的操作而言，本次操作的结果就是 last 的）
        self.current_operation = None

    def cancel_img(self):
        """
        “取消”按钮事件
        :return:
        """
        self.control.hide()
        if self.current_operation in ["clip", "blur"]:
            self.img_display.clearRect()
            self.img_display.flag = False  # 标记 img_display 不能绘制矩形，从而禁止选择裁剪区域
        elif self.current_operation == "lightness":
            self.slider_lightness.setValue(int((self.lightness_max + self.lightness_min) / 2))
        self.current_img = self.last_img
        self.showImage(self.current_img)
        self.current_operation = None

    def correction_img(self):
        """
        矫正事件重写
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        gray = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # 霍夫变换
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 0)
        rotate_angle = 0
        for rho, theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            if x1 == x2 or y1 == y2:
                continue
            t = float(y2 - y1) / (x2 - x1)
            rotate_angle = math.degrees(math.atan(t))
            if rotate_angle > 45:
                rotate_angle = -90 + rotate_angle
            elif rotate_angle < -45:
                rotate_angle = 90 + rotate_angle
        rotate_img = ndimage.rotate(self.current_img, rotate_angle)
        self.current_img = rotate_img
        self.showImage(self.current_img)
        self.current_operation == "correction"
        self.control.show()

    def horizontal_flip_img(self):
        """
        水平翻转
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        flipped_img = cv2.flip(self.current_img, 1)
        self.current_img = flipped_img
        self.showImage(self.current_img)
        self.current_operation == "flip"
        self.control.show()

    def vertical_flip_img(self):
        """
        垂直翻转
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        flipped_img = cv2.flip(self.current_img, 1)
        self.current_img = flipped_img
        self.showImage(self.current_img)
        self.current_operation == "flip"
        self.control.show()

    def diagonal_flip_img(self):
        """
        对角线翻转
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        flipped_img = cv2.flip(self.current_img, -1)
        self.current_img = flipped_img
        self.showImage(self.current_img)
        self.current_operation == "flip"
        self.control.show()

    def base_color_img_blue_to_red(self):
        """
        换成红底
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        img = cv2.resize(self.current_img, None, fx=1, fy=1)
        rows, cols, channels = img.shape
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([90, 70, 70])
        upper_blue = np.array([110, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=1)
        dilate = cv2.dilate(erode, None, iterations=1)
        for i in range(rows):
            for j in range(cols):
                if erode[i, j] == 255:  # 像素点为255表示的是白色，我们就是要将白色处的像素点，替换为红色
                    img[i, j] = (0, 0, 255)  # 此处替换颜色，为BGR通道，不是RGB通道
        self.current_img = img
        self.showImage(self.current_img)
        self.current_operation == "base_color"
        self.control.show()

    def base_color_img_blue_to_white(self):
        """
        蓝底转白底
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        img = cv2.resize(self.current_img, None, fx=1, fy=1)
        rows, cols, channels = img.shape
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([90, 70, 70])
        upper_blue = np.array([110, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=1)
        dilate = cv2.dilate(erode, None, iterations=1)
        for i in range(rows):
            for j in range(cols):
                if erode[i, j] == 255:  # 像素点为255表示的是白色，我们就是要将白色处的像素点，替换为红色
                    img[i, j] = (255, 255, 255)  # 此处替换颜色，为BGR通道，不是RGB通道
        self.current_img = img
        self.showImage(self.current_img)
        self.current_operation == "base_color"
        self.control.show()

    def base_color_img_red_to_blue(self):
        """
        蓝底转白底
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        img = cv2.resize(self.current_img, None, fx=1, fy=1)
        rows, cols, channels = img.shape
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([0, 100, 0])
        upper_blue = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=2)
        dilate = cv2.dilate(erode, None, iterations=2)
        for i in range(rows):
            for j in range(cols):
                if erode[i, j] == 255:  # 像素点为255表示的是白色，我们就是要将白色处的像素点，替换为红色
                    img[i, j] = (219, 142, 67)  # 此处替换颜色，为BGR通道，不是RGB通道
        self.current_img = img
        self.showImage(self.current_img)
        self.current_operation == "base_color"
        self.control.show()

    def base_color_img_red_to_white(self):
        """
        蓝底转白底
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        img = cv2.resize(self.current_img, None, fx=1, fy=1)
        rows, cols, channels = img.shape
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([0, 100, 0])
        upper_blue = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=2)
        dilate = cv2.dilate(erode, None, iterations=2)
        for i in range(rows):
            for j in range(cols):
                if erode[i, j] == 255:  # 像素点为255表示的是白色，我们就是要将白色处的像素点，替换为红色
                    img[i, j] = (255, 255, 255)  # 此处替换颜色，为BGR通道，不是RGB通道
        self.current_img = img
        self.showImage(self.current_img)
        self.current_operation == "base_color"
        self.control.show()

    def base_color_img_white_to_red(self):
        """
        蓝底转白底
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        img = cv2.resize(self.current_img, None, fx=1, fy=1)
        rows, cols, channels = img.shape
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([0, 0, 200])
        upper_blue = np.array([180, 30, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=2)
        dilate = cv2.dilate(erode, None, iterations=2)
        for i in range(rows):
            for j in range(cols):
                if erode[i, j] == 255:  # 像素点为255表示的是白色，我们就是要将白色处的像素点，替换为红色
                    img[i, j] = (0, 0, 255)  # 此处替换颜色，为BGR通道，不是RGB通道
        self.current_img = img
        self.showImage(self.current_img)
        self.current_operation == "base_color"
        self.control.show()

    def base_color_img_white_to_blue(self):
        """
        蓝底转白底
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        img = cv2.resize(self.current_img, None, fx=1, fy=1)
        rows, cols, channels = img.shape
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([0, 0, 200])
        upper_blue = np.array([180, 30, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # 腐蚀膨胀
        erode = cv2.erode(mask, None, iterations=2)
        dilate = cv2.dilate(erode, None, iterations=2)
        for i in range(rows):
            for j in range(cols):
                if erode[i, j] == 255:  # 像素点为255表示的是白色，我们就是要将白色处的像素点，替换为红色
                    img[i, j] = (219, 142, 67)  # 此处替换颜色，为BGR通道，不是RGB通道
        self.current_img = img
        self.showImage(self.current_img)
        self.current_operation == "base_color"
        self.control.show()

    def size_one_img(self):
        """
        一寸照
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        size_one_img = cv2.resize(self.current_img, (295, 413))
        self.current_img = size_one_img
        self.showImage(self.current_img)
        self.current_operation == "size"
        self.control.show()

    def size_two_img(self):
        """
        二寸照
        :return:
        """
        if self.current_img is None:
            self.__show_warning_message_box("未选择图片")
            return
        size_one_img = cv2.resize(self.current_img, (413, 626))
        self.current_img = size_one_img
        self.showImage(self.current_img)
        self.current_operation == "size"
        self.control.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
