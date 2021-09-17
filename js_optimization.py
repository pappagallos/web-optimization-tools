import os

# 변환할 파일 경로 정의
import re

global path
path = "/Users/leewoojin/Desktop/isoi-opti"

global sourceFileList
sourceFileList = []

# 디렉토리 리스트
global directoryPathList
directoryPathList = []

# 변환시킬 파일 확장자명 리스트 정의
global __AllowFileExtensionList
__AllowFileExtensionList = ["js", "JS", "txt", "TXT"]


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

            if filename.find(".config") >= 0 or filename.find("DS_Store") >= 0 or filename.find(
                    "_app.js") >= 0 or filename.find("_document.js") >= 0:
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
        # 1. <img * /> 태그 앞 뒤로 다른 태그가 있는지 검사하고 있으면 \n<img * />\n 으로 수정해준다.
        sourceStore = []
        sourceFile = open(dirPath, "r+")
        sourceLines = sourceFile.readlines()

        for line in sourceLines:
            # [1] 한 줄을 읽어와서 스페이스바를 기준으로 자른다.
            splitLine = line.split(" ")

            # 스페이스바 수만큼 공백이 추가될 변수
            emptyLine = ""
            # 탭을 나타내는 공백 변수
            tabLine = "    "

            # [2] 소스 라인에 공백 라인이 어느정도 있는지 가늠하기 위해 반복문을 돌려 검사
            emptyCounter = 0
            for index, value in enumerate(splitLine):
                # <img 태그가 나타날 때까지 반복문을 돌리는데 나타나면 emptyCounter 에 (index - 1) 한 수를 초기화, 그리고 탈출
                if value.find("<img") >= 0:
                    emptyCounter = index - 1
                    break

            # [3] 위에서 구한 emptyCounter 를 이용해서 emptyCounter 수 만큼 공백을 추가하여 수정할 때도 기존 소스의 공백 라인을 유지시켜준다.
            if line.find("<img") >= 0:
                for i in range(emptyCounter):
                    emptyLine += " "

            # [4] 위에서 splitLine 해서 나눈 리스트들을 반복문을 돌려 하나씩 <img 태그가 존재하는지 검사하여
            # <img 태그가 0번째 인덱스가 아닌 1 이상의 인덱스에 존재한다면 앞 라인에 다른 태그가 존재한다는 의미이므로 \n<img 로 변경해준다.
            for index, value in enumerate(splitLine):
                localIndex = value.find("<img")

                # 이 부분이 \n<img 로 변경해주는 부분, 변경하고 반복문 탈출
                if localIndex >= 1:
                    splitLine[index] = re.sub(r"\<img", "\n" + emptyLine + tabLine + "<img", value)
                    break

            # [5] 다시 Join 하여 리스트들을 문자열로 합치고 newEndSourceLine 변수에 초기화한다.
            newStartSourceLine = " ".join(splitLine)
            newEndSourceLine = newStartSourceLine

            # [6] newStartSourceLine 변수의 데이터에 만약 /> 가 존재한다면 /> 의 시작 인덱스로부터 +3 을 해줘서
            # newStartSourceLine의 총 글자 개수 보다 적다면(/> 의 마지막 인덱스 위치를 의미) <img * /> 앞에 또 다른 태그가 있다는 의미이므로 <img * />\n 을 해준다.
            if newStartSourceLine.rfind("/>") + 3 < newStartSourceLine.__len__():
                newEndSourceLine = re.sub(r"\/\>", "/>\n" + emptyLine, newStartSourceLine)

            # [7] 그리고 파일에 추가하기 위해 기존의 라인에 현재 가공한 데이터를 추가해준다.
            sourceStore = sourceStore + [newEndSourceLine]

        sourceFile.seek(0)
        sourceFile.writelines(sourceStore)
        sourceFile.truncate()
        sourceFile.close()

        # 2. 이제 img 태그가 시작하고 끝나는 start, end의 row 인덱스와 <img 가 시작하는 글자 인덱스, /> 끝나는 글자 인덱스를 구한다.
        sourceFile2 = open(dirPath, "r")
        sourceLines2 = sourceFile2.readlines()

        for line in sourceLines2:
            # regLine = re.findall(r'''[(\<)]{1}img\b[a-zA-Z0-9\_\.\=\{\}\'\"\/\+ ]*[(\/\>)|(\>)]{1}''', line)
            # print(regLine)

            if rowCounter >= scanStartIndex:
                # [1] <img의 시작 인덱스를 구한다.
                if startIndex == -1:
                    startIndex = line.find("<img")

                    # [2] 만약 없으면 다음 라인을 검사한다.
                    if startIndex == -1:
                        rowCounter += 1
                        sourceStore = sourceStore + [line]

                        continue
                    else:
                        # [3] 만약 있으면 rowCounter의 값을 startRowIndex에 초기화 한다.
                        startRowIndex = rowCounter

                # [4] <img 의 끝나는 부분인 /> 혹은 > 의 시작 인덱스를 구한다.
                if endIndex == -1:
                    endIndex = line.find("/>")
                    if endIndex == -1:
                        endIndex = line.find(">")

                    # [5] 만약 없으면 다음 라인으로 이동하여 다시 /> 혹은 > 가 있는지 검사한다.
                    if endIndex == -1:
                        rowCounter += 1
                        sourceStore = sourceStore + [line]

                        continue
                    else:
                        # [6] 만약 있으면 endIndex 를 /> 이 두개의 글자 수를 포함한 2를 더한 rowCounter의 값을 endRowIndex에 초기화 한다.
                        endIndex += 2
                        endRowIndex = rowCounter
                        print("endRowIndex, ", endRowIndex)

            else:
                rowCounter += 1

        sourceFile2.close()

        # 3. 재귀 함수 탈출용 로직
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
            sourceFile3 = open(dirPath, "r+")
            sourceLines3 = sourceFile3.readlines()

            for rowIndex, line in enumerate(sourceLines3):
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
                        propertyList = []
                        for rowIndex2, line2 in enumerate(sourceLines3):
                            if startRowIndex <= rowIndex2 <= endRowIndex:
                                regLine2 = re.findall(r'''[(\<)]{1}img\b[a-zA-Z0-9\_\.\=\{\}\'\"\/\+ ]*[(\/\>)|(\>)]{1}''', line2)[0]
                                propertyList.append(re.findall(r'''[a-zA-Z]*\b\=[\{\"\'][a-zA-Z0-9_.+\'\"\/ ]*[\}\"\']''', regLine2))
                                print("propertyList, ", propertyList)

                        srcContent = ""
                        stringifyProperty = []
                        for propertyContents in propertyList:
                            for propertyContent in propertyContents:
                                if propertyContent.find("src=") == -1:
                                    stringifyProperty.append(propertyContent)

                                elif propertyContent.find("src=") >= 0:
                                    srcContent = re.sub(r'''(src=)''', "", propertyContent)
                                    webpContent = re.sub(r'''(\.jpg)|(\.jpeg)|(\.png)|(\.JPG)|(\.JPEG)|(\.PNG)''', ".webp", srcContent)

                        stringifyProperty = " ".join(stringifyProperty)
                        print("stringifyProperty, ", stringifyProperty)

                        newSourceLine = f"\n{emptyLine}<picture>\n" \
                                        f"{emptyLine + tabLine}<source srcSet={webpContent} {stringifyProperty} type='image/webp' />\n" \
                                        f"{emptyLine + tabLine}<source srcSet={srcContent} {stringifyProperty} type='image/{extension}' />\n" \
                                        f"{emptyLine + tabLine}<img src={srcContent} {stringifyProperty} />\n" \
                                        f"{emptyLine}</picture>\n"
                        sourceStore = sourceStore + [newSourceLine]
                        isConvert = True
                    else:
                        sourceStore = sourceStore + [""]
                else:
                    sourceStore = sourceStore + [line]

            sourceFile3.seek(0)
            sourceFile3.writelines(sourceStore)
            sourceFile3.truncate()

            sourceFile3.close()

        print(f"dirPath : {dirPath}, {scanStartIndex}")

        optimizationRule(dirPath, startRowIndex + 5)

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
