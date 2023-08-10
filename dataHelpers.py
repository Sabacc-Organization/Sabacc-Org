def listToStr(l, sep=","):
    s = ""
    for item in l:
        s += str(item)
        s += sep

    st = s[0:len(s) - 1]
    return st

def strListMod(strList, index, val, sep=","):
    listStr = strList.split(sep)
    listStr[index] = val
    return listToStr(listStr, sep)

def strListRead(strList, index, sep=",", default=""):
    listStr = strList.split(sep)
    if listStr[index] != "":
        return listStr[index]
    else:
        return default

def readIntValStrList(strList, index, sep=",", defVal=0):
    val = strListRead(strList, index, sep=sep)
    try:
        return int(val)
    except:
        return defVal
    
def strListPop(strList, index, sep=","):
    listStr = strList.split(sep)
    listStr.pop(index)
    return listToStr(listStr, sep)

def strListRemove(strList, val, sep=","):
    listStr = strList.split(sep)

    listStr.remove(val)

    return listToStr(listStr, sep)

def strListAppend(strList, item, sep=","):
    listStr = []

    if strList != None:
        listStr = strList.split(sep)
    
    listStr.append(item)

    return listToStr(listStr, sep)