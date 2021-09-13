import os

# 변환할 파일 경로 정의
import re

global path
path = "/Users/leewoojin/Desktop/web-optimization-tools"

global sourceFileList
sourceFileList = []

# 디렉토리 리스트
global directoryPathList
directoryPathList = []

# 변환시킬 파일 확장자명 리스트 정의
global __AllowFileExtensionList
__AllowFileExtensionList = ["js", "JS"]


def scanDirectory(dirPath):
    filenames = os.listdir(dirPath)

    for filename in filenames:
        filePath = os.path.join(dirPath, filename)

        if filename.find("node_modules") >= 0 or filename.find("DS_Store") >= 0 or filename.find(".") >= 0:
            continue
        else:
            directoryPathList.append(filePath)
            scanDirectory(filePath)

    print("[LOG] directory list. ", directoryPathList)

    return


def scanSourceFiles():
    for dirPath in directoryPathList:
        filenames = os.listdir(dirPath)

        for filename in filenames:
            filePath = os.path.join(dirPath, filename)

            if filename.find(".config") >= 0 or filename.find("DS_Store") >= 0 or filename.find("_app.js") >= 0 or filename.find("_document.js") >= 0:
                continue
            else:
                extensionType = filename.split(".").pop()

                for extension in __AllowFileExtensionList:
                    if extension == extensionType:
                        print("[LOG] successful find file. ", filePath)
                        sourceFileList.append(filePath)
                        break

    print("[LOG] convert list. ", sourceFileList)


def optimizationRule(dirPath, scanStartIndex):
    isValid = False
    isConvert = False
    rowCounter = 0
    startRowIndex = -1
    endRowIndex = -1
    startIndex = -1
    endIndex = -1

    for extension in __AllowFileExtensionList:
        if dirPath.find(f".{extension}") >= 0:
            isValid = True
            break

    if isValid:
        sourceFile = open(dirPath, "r")
        sourceLines = sourceFile.readlines()

        for line in sourceLines:
            if rowCounter >= scanStartIndex:
                # <img의 시작 인덱스를 구한다.
                if startIndex == -1:
                    startIndex = line.find("<img")

                    # 만약 없으면 다음 라인을 검사한다.
                    if startIndex == -1:
                        rowCounter += 1
                        continue
                    else:
                        # 만약 있으면 rowCounter의 값을 startRowIndex에 초기화 한다.
                        startRowIndex = rowCounter

                # <img 의 끝나는 부분인 />의 시작 인덱스를 구한다.
                if endIndex == -1:
                    endIndex = line.find("/>")

                    # 만약 없으면 다음 라인으로 이동하여 다시 /> 가 있는지 검사한다.
                    if endIndex == -1:
                        rowCounter += 1
                        continue
                    else:
                        endIndex += 2
                        endRowIndex = rowCounter

            else:
                rowCounter += 1

        sourceFile.close()

        if startRowIndex >= 0 and endRowIndex >= 0:
            print(f"startRowIndex : {startRowIndex} / endRowIndex : {endRowIndex}")
        else:
            # 더 이상 다음 img 태그를 찾는 startRowIndex, endRowIndex가 존재하지 않는다면
            # 읽고 있는 소스 파일에는 다음으로 존재하는 img 태그가 없는 것으로 간주하고 재귀 함수를 탈출한다.
            return

        # 여기까지 왔다면 startIndex와 endIndex 그리고 rowStartIndex, rowEndIndex가 구해졌다는 의미이므로 이제 최적화 과정을 진행한다.
        if startIndex != -1 and endIndex != -1 and startRowIndex != -1 and endRowIndex != -1:
            # 이제 webP 크로스 브라우징을 위해 적용할 이미지 소스를 optimizationRule가 직접 반영해준다.
            sourceStore = []
            sourceFile = open(dirPath, "r+")
            sourceLines = sourceFile.readlines()

            for rowIndex, line in enumerate(sourceLines):
                if startRowIndex <= rowIndex <= endRowIndex:
                    # 파일 확장자 구하기
                    extension = "jpg"
                    if line.find(".jpg") >= 0:
                        extension = "jpg"
                    elif line.find(".png") >= 0:
                        extension = "png"
                    elif line.find(".gif") >= 0:
                        extension = "gif"

                    emptyLine = ""
                    tabLine = "    "
                    for i in range(startIndex):
                        emptyLine += " "

                    if not isConvert:
                        srcIndex = -1
                        altIndex = -1
                        reg = "/(src=)|(alt=)|(\")|(\')/"

                        lineArr = line.split(" ")
                        print(lineArr)

                        scanIndex = 0
                        while srcIndex == -1 and altIndex == -1:
                            for lineItem in lineArr:
                                if lineItem.find("src=") >= 0:
                                    srcIndex = scanIndex
                                elif lineItem.find("alt=") >= 0:
                                    altIndex = scanIndex

                                scanIndex += 1

                        print("srcIndex", srcIndex)
                        print("altIndex", altIndex)

                        textSrc = re.sub(r"src=", "", lineArr[srcIndex])
                        textAlt = re.sub(r"alt=|\"|\'", "", lineArr[altIndex])

                        print("textSrc : ", textSrc)
                        print("textAlt : ", textAlt)

                        newSourceLine = f"\n{emptyLine}{{/* webP 확장자 크로스 브라우징 지원 소스 */}}\n" \
                                        f"{emptyLine}<picture>\n" \
                                        f"{emptyLine + tabLine}<source srcSet={textSrc} type='image/webp' />\n" \
                                        f"{emptyLine + tabLine}<source srcSet={{process.env.NEXT_PUBLIC_CFRONT_V4 + '/mobile/product/line/factman01.{extension}'}} type='image/{extension}' />\n" \
                                        f"{emptyLine + tabLine}<img src={{process.env.NEXT_PUBLIC_CFRONT_V4 + '/mobile/product/line/factman01.{extension}'}} alt='' />\n" \
                                        f"{emptyLine}</picture>\n"
                        sourceStore = sourceStore + [newSourceLine]
                        isConvert = True
                    else:
                        sourceStore = sourceStore + [""]
                else:
                    sourceStore = sourceStore + [line]

            sourceFile.seek(0)
            sourceFile.writelines(sourceStore)
            sourceFile.truncate()

            sourceFile.close()

        print(f"dirPath : {dirPath}, {scanStartIndex}")

        optimizationRule(dirPath, startRowIndex + 6)

        return
    else:
        print(f"[WARN] {dirPath} is not file. passed optimization.")

    return


def runOptimization():
    for dirPath in sourceFileList:
        print(f"[{dirPath}]")
        optimizationRule(dirPath, 0)

    return


scanDirectory(path)
directoryPathList.append(path)

scanSourceFiles()
runOptimization()
