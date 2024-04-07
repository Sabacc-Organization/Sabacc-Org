""" File full of functions for dealing with strings and lists """

# Convert list to string
def listToStr(l, sep=","):
    s = ""
    for item in l:
        s += str(item)
        s += sep

    st = s[0:len(s) - 1]
    return st

# Modify a value in a list represented as a string
def strListMod(strList, index, val, sep=","):
    listStr = strList.split(sep)
    listStr[index] = val
    return listToStr(listStr, sep)

# Read a value in a list represented as a string
def strListRead(strList, index, sep=",", default=""):
    listStr = strList.split(sep)
    if listStr[index] != "":
        return listStr[index]
    else:
        return default

# Read an integer value in a list represented as a string
def readIntValStrList(strList, index, sep=",", defVal=0):
    val = strListRead(strList, index, sep=sep)
    try:
        return int(val)
    except:
        return defVal
    
# Pop a value in a list represented as a string
def strListPop(strList, index, sep=","):
    listStr = strList.split(sep)
    listStr.pop(index)
    return listToStr(listStr, sep)

# Remove a value in a list represented as a string
def strListRemove(strList, val, sep=","):
    listStr = strList.split(sep)

    listStr.remove(val)

    return listToStr(listStr, sep)

# Append a value to a list represented as a string
def strListAppend(strList, item, sep=","):
    listStr = []

    if strList != None:
        listStr = strList.split(sep)
    
    listStr.append(item)

    return listToStr(listStr, sep)

# "Shift" items in a list (0 becomes 1, 1 becomes 2, 2 becomes 0)
def shiftList(arr):
    l = arr.copy()
    l.insert(0, l[len(l) - 1])
    l.pop(len(l) - 1)
    return l