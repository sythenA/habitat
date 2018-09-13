
def toUnicode(string):
    try:
        string = unicode(string.decode('utf-8'))
    except(UnicodeEncodeError):
        try:
            string = unicode(string.decode('big5'))
        except(UnicodeEncodeError):
            return unicode(string)

    return string
