import os

# 변환할 파일 경로 정의
global path
path = "/Users/leewoojin/Desktop/web-optimization-tools"

global sourceFileList
sourceFileList = []

# 디렉토리 리스트
global directoryPathList
directoryPathList = []

# 변환시킬 파일 확장자명 리스트 정의
global __AllowFileExtensionList
__AllowFileExtensionList = ["js", "JS", "css", "CSS"]


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


def optimizationRule(dirPath, startRowIndex, endRowIndex, startIndex, endIndex):
    sourceStore = []
    sourceFile = open(dirPath, "r+")
    sourceLines = sourceFile.readlines()

    for rowIndex, line in enumerate(sourceLines):
        print("rowIndex : ", rowIndex, ", line ", line)
        if startRowIndex <= rowIndex <= endRowIndex:
            # 파일 확장자 구하기
            extension = ".jpg"
            if line.find(".jpg") >= 0:
                extension = ".jpg"
            elif line.find(".png") >= 0:
                extension = ".png"
            elif line.find(".gif") >= 0:
                extension = ".gif"

            newSourceLine = "\n<picture>\n"\
                            "수정할 내용"\
                            "\n</picture>\n"
            sourceStore = sourceStore + [newSourceLine]
        else:
            sourceStore = sourceStore + [line]

    sourceFile.seek(0)
    sourceFile.writelines(sourceStore)
    sourceFile.truncate()

    sourceFile.close()

    return


def runOptimization():
    isValid = False

    for dirPath in sourceFileList:
        rowCounter = -1
        startRowIndex = -1
        endRowIndex = -1
        startIndex = -1
        endIndex = -1

        for extension in __AllowFileExtensionList:
            if dirPath.find(f".{extension}") >= 0:
                isValid = True
                break

        if isValid:
            isValid = False

            sourceFile = open(dirPath, "r")
            sourceLines = sourceFile.readlines()

            print(f"[{sourceFile.name}]")

            for line in sourceLines:
                rowCounter += 1
                print()

                # <img의 시작 인덱스를 구한다.
                if startIndex == -1:
                    startIndex = line.find("<img")

                    # 만약 없으면 다음 라인을 검사한다.
                    if startIndex == -1:
                        continue
                    else:
                        # 만약 있으면 rowCounter의 값을 startRowIndex에 초기화 한다.
                        startRowIndex = rowCounter

                # <img 의 끝나는 부분인 />의 시작 인덱스를 구한다.
                if endIndex == -1:
                    endIndex = line.find("/>")

                    # 만약 없으면 다음 라인으로 이동하여 다시 /> 가 있는지 검사한다.
                    if endIndex == -1:
                        continue
                    else:
                        endIndex += 2
                        endRowIndex = rowCounter

                # 여기까지 왔다면 startIndex와 endIndex 그리고 rowStartIndex, rowEndIndex가 구해졌다는 의미이므로 이제 최적화 과정을 진행한다.
                if startIndex != -1 and endIndex != -1 and startRowIndex != -1 and endRowIndex != -1:
                    # 이제 webP 크로스 브라우징을 위해 적용할 이미지 소스를 optimizationRule가 직접 반영해준다.
                    optimizationRule(dirPath, startRowIndex, endRowIndex, startIndex, endIndex)

                    # 다음 라인에도 img 태그가 있을 수 있으므로 다음 라인을 위해 최적화하기 위한 정보를 모두 -1로 초기화 해준다.
                    startRowIndex = -1
                    endRowIndex = -1
                    startIndex = -1
                    endIndex = -1
                else:
                    continue

            sourceFile.close()
        else:
            print(f"[WARN] {dirPath} is not file. passed optimization.")
            continue

    return


scanDirectory(path)
directoryPathList.append(path)

scanSourceFiles()
runOptimization()
