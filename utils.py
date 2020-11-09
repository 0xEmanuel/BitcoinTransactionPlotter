def extractStringBetween(inputString,startString, endString):
    if startString != "":
        posStart = inputString.find(startString)
    else:
        posStart = 0

    if posStart == -1:
        return ""

    if endString != "":
        posEnd = inputString.find(endString, posStart+len(startString)) #start searching from posStart
    else:
        posEnd = len(inputString)

    if posEnd == -1:
        return ""

    return inputString[posStart + len(startString):posEnd]