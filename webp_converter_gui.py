import sys
import os
import time
from PIL import Image
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt5 import uic


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form = resource_path('converter.ui')
form_class = uic.loadUiType(form)[0]

path = ""


# 스레드 생성하여 변환 실행
class Thread(QThread):
    # 이미지 리스트
    imagePathList = []

    # 디렉토리 리스트
    directoryPathList = []

    # 변환 개수
    convertCounter = 0

    # 변환시킬 파일 확장자명 리스트 정의
    __AllowFileExtensionList = ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG"]

    # 부모에게 전달할 프로그레스 값
    progressValue = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Thread, self).__init__(parent)
        self.parent = parent

    def run(self):
        global path

        self.scanDirectory(path)
        self.directoryPathList.append(path)
        self.scanImageFiles()

        self.parent.progressBar.setMaximum(self.imagePathList.__len__())

        self.runConverter()

    def scanDirectory(self, dirPath):
        filenames = os.listdir(dirPath)

        for filename in filenames:
            filePath = os.path.join(dirPath, filename)

            if filename.find("DS_Store") >= 0 or filename.find(".") >= 0:
                continue
            else:
                self.directoryPathList.append(filePath)
                self.scanDirectory(filePath)

        self.parent.textBrowser_log.append(f"[LOG] directory list. {self.directoryPathList}")
        time.sleep(0.02)
        self.scrollToBottom()

        return

    def scanImageFiles(self):
        for dirPath in self.directoryPathList:
            filenames = os.listdir(dirPath)

            for filename in filenames:
                filePath = os.path.join(dirPath, filename)
                extensionType = filename.split(".").pop()

                for extension in self.__AllowFileExtensionList:
                    if extension == extensionType:
                        self.imagePathList.append(filePath)
                        self.parent.textBrowser_log.append(f"[LOG] successful find image file. {filePath}")
                        time.sleep(0.02)
                        self.scrollToBottom()
                        break

        self.parent.textBrowser_log.append(f"[LOG] convert image list. {self.imagePathList}")
        time.sleep(0.02)
        self.scrollToBottom()

    def runConverter(self):
        for imagePath in self.imagePathList:
            image = Image.open(imagePath)

            self.parent.textBrowser_log.append(
                f"[CONVERT] fileName: {image.filename} | format: {image.format} | size: {image.size}byte | width: {image.width}px | height: {image.height}px")
            time.sleep(0.02)
            self.scrollToBottom()

            imageFilePath = image.filename.split(".")[0]

            savePath = imageFilePath + ".webp"

            if image.format == "PNG":
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")

            image.save(savePath, "WEBP")

            # 압축하기 위한 로직, 압축하시려면 주석 해체 후 사용하세요.
            # compressImage = Image.open(savePath)
            # compressImage.save(savePath, quality=90)

            image.close()

            # 압축하기 위한 로직, 압축하시려면 주석 해체 후 사용하세요.
            # compressImage.close()

            self.parent.textBrowser_log.append(f"[CONVERT COMPLETE] webp image save complete. | {savePath}")
            time.sleep(0.02)
            self.scrollToBottom()

            convertCount = self.parent.progressBar.value()
            convertCount += 1
            self.progressValue.emit(convertCount)
            time.sleep(0.02)

    def scrollToBottom(self):
        self.parent.textBrowser_log.verticalScrollBar().setValue(
            self.parent.textBrowser_log.verticalScrollBar().maximum())


class WEBPConverterApp(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.thread = Thread(self)
        self.setupUi(self)
        self.toolButton_finder.clicked.connect(self.findDirectoryFunction)
        self.pushButton_convert.clicked.connect(self.convertFunction)
        self.pushButton_quit.clicked.connect(self.quitFunction)

    def quitFunction(self):
        QCoreApplication.instance().quit()

    def findDirectoryFunction(self):
        global path
        path = QFileDialog.getExistingDirectory(self, "Select Directory")

        self.textBrowser_folder_path.setPlainText(path)

    def convertFunction(self):
        global path

        if path == "":
            QMessageBox.warning(self, "Warning", "Please select the folder with images to convert first.")
            return

        confirm = QMessageBox.question(self, "Question", "Would you like to proceed with the transformation?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            self.textBrowser_log.clear()

            self.thread.progressValue.connect(self.setProgressValue)
            self.thread.start()

    def setProgressValue(self, value):
        self.progressBar.setValue(value)

        if self.thread.imagePathList.__len__() == value:
            QMessageBox.information(self, "Success", "Successfully converted.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = WEBPConverterApp()
    myApp.show()
    app.exec_()
