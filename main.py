import sys, atexit, cv2, time, glob, os, math

from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
from PyQt5 import uic

running = True

import camera1, camera2, camera3, camera4

frame1 = None
frame2 = None
frame3 = None
frame4 = None
ret = None
rgbImage = None
outputFrame1 = None
outputFrame2 = None
outputFrame3 = None
outputFrame4 = None


class QLabelClickable(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super(QLabelClickable, self).__init__(parent)

    def mousePressEvent(self, event):
        self.ultimo = "Clic"

    def mouseReleaseEvent(self, event):
        if self.ultimo == "Clic":
            QTimer.singleShot(QApplication.instance().doubleClickInterval(), self.performSingleClickAction)
        else:
            self.clicked.emit(self.ultimo)

    def mouseDoubleClickEvent(self, event):
        self.ultimo = "Doble Clic"

    def performSingleClickAction(self):
        if self.ultimo == "Clic": self.clicked.emit(self.ultimo)

    def enterEvent(self, event):
        self.setStyleSheet(
            "color: black; background-color: black; border-radius: 3px; border-style: none; border: 1px solid lime;")

    def leaveEvent(self, event):
        self.setStyleSheet(
            "color: black; background-color: black; border-radius: 3px; border-style: none; border: 1px solid black;")


class Overlay(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.setFixedSize(1024, 600)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 187)))

        amount_of_circles = 12

        for i in range(amount_of_circles):
            painter.setPen(QPen(Qt.NoPen))
            if (self.counter) % amount_of_circles == i:
                painter.setBrush(QBrush(QColor(56, 165, 59)))
            elif (self.counter) % amount_of_circles == i + 4:
                painter.setBrush(QBrush(QColor(56, 165, 59)))
            elif (self.counter) % amount_of_circles == i + 8:
                painter.setBrush(QBrush(QColor(56, 165, 59)))
            elif (self.counter) % amount_of_circles == i - 4:
                painter.setBrush(QBrush(QColor(56, 165, 59)))
            elif (self.counter) % amount_of_circles == i - 8:
                painter.setBrush(QBrush(QColor(56, 165, 59)))
            else:
                painter.setBrush(QBrush(QColor(205 - (i * 10), 56, 59)))
            # else: painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width() / 2 + 50 * math.cos(2 * math.pi * i / amount_of_circles) - 20,
                self.height() / 2.2 + 50 * math.sin(2 * math.pi * i / amount_of_circles) - 20,
                20, 20)
            painter.setPen(QPen(QColor(127, 127, 127), 1))
            painter.setFont(QFont(None, 22, 1, False))
            if (self.counter) % amount_of_circles == i:
                w = "Starting."
            elif (self.counter) % amount_of_circles == i + (amount_of_circles / 2 - 1):
                w = "Starting.."
            elif (self.counter) % amount_of_circles == i + (amount_of_circles - 3):
                w = "Starting..."
            else:
                w = 'Starting'
            painter.drawText(int(self.width() / 2 - 55), int(self.height() / 1.5), 160, 50, Qt.AlignLeft | Qt.AlignLeft,
                             w)

        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(100)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()
        if self.counter == 20:
            self.killTimer(self.timer)
            self.close()


class mainwindowUI(QMainWindow):

    def __init__(self):
        super(mainwindowUI, self).__init__()
        self.show()
        self.setFixedSize(1024, 600)
        self.overlay = Overlay(self)
        self.overlay.show()

        self.timer = self.startTimer(50)
        self.counter = 0

        self.isCamViewFullScreen = False
        self.center()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def timerEvent(self, event):
        self.counter += 1
        self.update()
        if self.counter == 60:
            self.overlay.hide()
            self.load_UI()
            self.start_cameras()

    def start_cameras(self):
        for i in range(len(self.lblCameras)):
            # if self.testDevice(i):
            if i == 0:
                th1 = Thread1(self.lblCameras[i], i)
                th1.changePixmap.connect(self.setImageCam)
                th1.start()
            elif i == 1:
                th2 = Thread2(self.lblCameras[i], i)
                th2.changePixmap.connect(self.setImageCam)
                th2.start()
            elif i == 2:
                th3 = Thread3(self.lblCameras[i], i)
                th3.changePixmap.connect(self.setImageCam)
                th3.start()
            elif i == 3:
                th4 = Thread4(self.lblCameras[i], i)
                th4.changePixmap.connect(self.setImageCam)
                th4.start()

    def load_UI(self):
        uic.loadUi('main.ui', self)

        '---------------------TOOL BAR---------------------'
        self.btnBackToMenu = self.findChild(QPushButton, 'btnBackToMenu')
        self.btnBackToMenu.clicked.connect(self.backToMenu)

        self.btnBackToCameras.clicked.connect(self.backToCameras)
        self.btnBackToCameras = self.findChild(QPushButton, 'btnBackToCameras')

        self.btnBackToMenu.setHidden(True)
        self.btnBackToCameras.setHidden(True)

        '---------------------CAMERAS---------------------'

        self.frameCamera = self.findChild(QFrame, 'frameCameras')
        self.cameraGrid = self.findChild(QGridLayout, 'cameraGrid')

        self.lblCam1 = QLabelClickable(self)
        self.lblCam2 = QLabelClickable(self)
        self.lblCam3 = QLabelClickable(self)
        self.lblCam4 = QLabelClickable(self)
        self.lblCameras = [self.lblCam1, self.lblCam2, self.lblCam3, self.lblCam4]

        for index, cam in enumerate(self.lblCameras):
            cam.setStyleSheet(
                "color: black; background-color: black; border-radius: 3px; border-style: none; border: 1px solid black;")
            cam.setAlignment(Qt.AlignCenter)
            cam.clicked.connect(partial(self.lblCamClicked, cam, index, True))

        colSize = 2
        # for i, camera in enumerate(glob.glob("/dev/video?") + 1): self.cameraGrid.addWidget(self.lblCameras[i], int(i / colSize), int(i % colSize))

        '''
        _______________
        |  0,0 | 0,1  |
        |   1  |  3   |
        |______|______|
        |  1,0 | 1,1  |
        |   2  |  4   |
        |______|______|
        '''
        self.cameraGrid.addWidget(self.lblCam1, 0, 0)
        self.cameraGrid.addWidget(self.lblCam2, 1, 0)
        self.cameraGrid.addWidget(self.lblCam3, 0, 1)
        self.cameraGrid.addWidget(self.lblCam4, 1, 1)

        '---------------------MAIN MENU---------------------'

        self.frameMainMenu = self.findChild(QFrame, 'frameMainMenu')

        self.btnCameras = self.findChild(QPushButton, 'btnCameras')
        self.btnCameras.clicked.connect(self.btnCamerasClicked)

        '---------------------MUSIC---------------------'

        self.frameMusic = self.findChild(QFrame, 'frameMusic')
        self.treeViewMusic = self.findChild(QTreeView, 'treeViewMusic')

        self.btnMusic = self.findChild(QPushButton, 'btnMusic')
        self.btnMusic.clicked.connect(self.btnMusicClicked)

        path = MUSIC_FOLDER

        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(QDir.rootPath())
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries | QDir.Dirs | QDir.Files)

        self.fileModel = QFileSystemModel()
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries | QDir.Dirs | QDir.Files)

        self.treeview = QTreeView()
        self.treeViewMusic.setModel(self.dirModel)
        self.treeViewMusic.setRootIndex(self.dirModel.index(path))

        self.listview = QListView()
        self.listview.setModel(self.fileModel)
        self.listview.setRootIndex(self.fileModel.index(path))

        self.treeViewMusic.clicked.connect(self.treeViewClicked)

        '---------------------DEFAULT SETTING---------------------'

        self.frameCamera.setHidden(True)
        self.frameMusic.setHidden(True)
        self.frameMainMenu.setHidden(False)

    def backToCameras(self):
        for i in range(len(self.lblCameras)): self.lblCameras[i].setHidden(False)
        self.btnCamerasClicked()
        self.isCamViewFullScreen = False

    def lblCamClicked(self, lbl, index, viewFullScreen):
        # print(index)
        if viewFullScreen:
            self.isCamViewFullScreen = True
            lbl.clicked.connect(partial(self.lblCamClicked, lbl, index, False))
            self.btnBackToMenu.setHidden(True)
            self.btnBackToCameras.setHidden(False)
            for i in range(len(self.lblCameras)): self.lblCameras[i].setHidden(True)
            lbl.setHidden(False)
        else:
            self.isCamViewFullScreen = False
            self.backToCameras()
            lbl.clicked.connect(partial(self.lblCamClicked, lbl, index, True))

    def btnCamerasClicked(self):
        self.frameCamera.setHidden(False)
        self.frameMainMenu.setHidden(True)
        self.frameMusic.setHidden(True)

        self.btnBackToMenu.setHidden(False)
        self.btnBackToCameras.setHidden(True)

    def btnMusicClicked(self):
        self.frameCamera.setHidden(True)
        self.frameMainMenu.setHidden(True)
        self.frameMusic.setHidden(False)

        self.btnBackToMenu.setHidden(False)
        self.btnBackToCameras.setHidden(True)

    def treeViewClicked(self, index):
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        print(path)
        self.listview.setRootIndex(self.fileModel.setRootPath(path))

    def backToMenu(self):
        self.frameCamera.setHidden(True)
        self.frameMainMenu.setHidden(False)
        self.frameMusic.setHidden(True)

        self.btnBackToMenu.setHidden(True)
        self.btnBackToCameras.setHidden(True)

    # @pyqtSlot(QObject, QImage, int)
    def setImageCam(self, label, image, index, name=None):
        if name == '404.png':
            self.cameraGrid.removeWidget(self.lblCameras[index])
            self.lblCameras[index].deleteLater()
            self.lblCameras[index] = None
            self.lblCameras.pop(index)
            return
        if self.isCamViewFullScreen:
            image = image.scaled(640, 480, Qt.KeepAspectRatio, Qt.FastTransformation)
        else:
            image = image.scaled(320, 240, Qt.KeepAspectRatio, Qt.FastTransformation)
        label.setFixedSize(image.width(), image.height())
        label.setPixmap(QPixmap.fromImage(image))


class Thread1(QThread):
    changePixmap = pyqtSignal(object, QImage, int, str)

    def __init__(self, lblCam, port):
        QThread.__init__(self)
        self.lblCam = lblCam
        self.port = port
        camera1.start_cam()

    @pyqtSlot()
    def run(self):
        while running:
            if running: frame1 = camera1.camRun()
            try:
                rgbImage = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.changePixmap.emit(self.lblCam, convertToQtFormat, self.port, '')
            except:
                self.lblCam.setFixedSize(1, 1)
                image = QImage('404.png')
                self.changePixmap.emit(self.lblCam, image, self.port, '404.png')
                break


class Thread2(QThread):
    changePixmap = pyqtSignal(object, QImage, int, str)

    def __init__(self, lblCam, port):
        QThread.__init__(self)
        self.lblCam = lblCam
        self.port = port
        camera2.start_cam()

    @pyqtSlot()
    def run(self):
        while running:
            if running: frame2 = camera2.camRun()
            try:
                rgbImage = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.changePixmap.emit(self.lblCam, convertToQtFormat, self.port, '')
            except:
                self.lblCam.setFixedSize(1, 1)
                image = QImage('404.png')
                self.changePixmap.emit(self.lblCam, image, self.port, '404.png')
                break


class Thread3(QThread):
    changePixmap = pyqtSignal(object, QImage, int, str)

    def __init__(self, lblCam, port):
        QThread.__init__(self)
        self.lblCam = lblCam
        self.port = port
        camera3.start_cam()

    @pyqtSlot()
    def run(self):
        while running:
            if running: frame3 = camera3.camRun()
            try:
                rgbImage = cv2.cvtColor(frame3, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.changePixmap.emit(self.lblCam, convertToQtFormat, self.port, '')
            except:
                self.lblCam.setFixedSize(1, 1)
                image = QImage('404.png')
                self.changePixmap.emit(self.lblCam, image, self.port, '404.png')
                break


class Thread4(QThread):
    changePixmap = pyqtSignal(object, QImage, int, str)

    def __init__(self, lblCam, port):
        QThread.__init__(self)
        self.lblCam = lblCam
        self.port = port
        camera4.start_cam()

    @pyqtSlot()
    def run(self):
        while running:
            if running: frame4 = camera4.camRun()
            try:
                rgbImage = cv2.cvtColor(frame4, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                self.changePixmap.emit(self.lblCam, convertToQtFormat, self.port, '')
            except:
                self.lblCam.setFixedSize(1, 1)
                image = QImage('404.png')
                self.changePixmap.emit(self.lblCam, image, self.port, '404.png')
                break


# def load_config_file(*args):
#     global config_json
#     for i, j in enumerate(args):
#         j.clear()
#         with open(config_file) as file:
#             config_json = json.load(file)
#             for d in config_json[0]['Default']: args[0].append(d)
#             for da in config_json[0]['Dark']: args[1].append(da)
#             for l in config_json[0]['Light']: args[2].append(l)
#             for c in config_json[0]['CSS']: args[3].append(c)
#             for g in config_json[0]['Last Genre']: args[4].append(g)
#             for al in config_json[0]['Last Algorithm']: args[5].append(al)
#             for th in config_json[0]['Last Theme']: args[6].append(th)
#             for dexp in config_json[0]['Default Export Path']: args[7].append(dexp)
#             for ts in config_json[0]['Toggle Sound On']: args[8].append(ts)


def exit_handler(): sys.exit()


MUSIC_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/Music/'

if not os.path.exists(MUSIC_FOLDER): os.mkdir(MUSIC_FOLDER)

if __name__ == '__main__':
    # load_config_file(DefaultMode, DarkMode, LightMode, CSSOn,
    #                  lastSelectedGenre, lastSelectedAlgorithm,
    #                  lastSelectedTheme, defaultExportPath, toggleSoundOn)
    atexit.register(exit_handler)
    app = QApplication(sys.argv)
    window = mainwindowUI()
    app.exec_()
