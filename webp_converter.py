# JPG, PNG, GIF 이미지들을 한 번에 WEBP로 변환하기 위한 유틸리티
from PIL import Image

import os

# 변환할 파일 경로 정의
global path

# 1. PNG, JPG, GIF 이미지들을 모두 서버에 있는 폴더 그대로 다운로드 받으신 뒤 특정 폴더 안에 넣으세요.
# 2. 넣으신 뒤 해당 폴더의 경로를 아래에 적어시고 실행해주세요.
# 3. 각 폴더별로 WEBP 확장자명의 이미지들이 생기신 것을 확인하실 수 있습니다.
path = "/Users/leewoojin/Desktop/imges"

# 이미지 변환이 필요한 이미지 경로 리스트
# JPG => WEBP
# PNG => WEBP
# GIF => WEBP
global imagePathList
imagePathList = []

# 디렉토리 리스트
global directoryPathList
directoryPathList = []

# 변환시킬 파일 확장자명 리스트 정의
global __AllowFileExtensionList
__AllowFileExtensionList = ["png", "PNG", "gif", "GIF", "jpg", "JPG", "jpeg", "JPEG"]


def scanDirectory(dirPath):
    filenames = os.listdir(dirPath)

    for filename in filenames:
        filePath = os.path.join(dirPath, filename)

        if filename.find("DS_Store") >= 0 or filename.find(".") >= 0:
            continue
        else:
            directoryPathList.append(filePath)
            scanDirectory(filePath)

    print("[LOG] directory list. ", directoryPathList)

    return


def scanImageFiles():
    for dirPath in directoryPathList:
        filenames = os.listdir(dirPath)

        for filename in filenames:
            filePath = os.path.join(dirPath, filename)
            extensionType = filename.split(".").pop();

            for extension in __AllowFileExtensionList:
                if extension == extensionType:
                    print("[LOG] successful find image file. ", filePath)
                    imagePathList.append(filePath)
                    break

    print("[LOG] convert image list. ", imagePathList)


def runConverter():
    for imagePath in imagePathList:
        image = Image.open(imagePath)

        print(
            f"[CONVERT] fileName: {image.filename} | format: {image.format} | size: {image.size}byte | width: {image.width}px | height: {image.height}px")

        imageFilePath = image.filename.split(".")[0]

        savePath = imageFilePath + ".webp"

        if image.format == "PNG":
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        image.save(savePath, "webp")

        # 압축하기 위한 로직, 압축하시려면 주석 해체 후 사용하세요.
        # compressImage = Image.open(savePath)
        # compressImage.save(savePath, quality=90)

        image.close()

        # 압축하기 위한 로직, 압축하시려면 주석 해체 후 사용하세요.
        # compressImage.close()

        print(f"[COMPLETE] webp image save complete. | {savePath}")


scanDirectory(path)
directoryPathList.append(path)

scanImageFiles()
runConverter()