def exercise1():
    # 1. Matching Decimal Numbers:
    return r"^-?([0-9]{3},?)*[0-9]{0,3}\.?[0-9]*e?[0-9]*$"

def exercise2():
    # 2. Matching Phone Numbers
    return r"[0-9]?\s?\(?([0-9]{3})\)?(-|\s)?[0-9]{3}(-|\s)?[0-9]{4}"

def exercise3():
    # 3. Matching Emails
    return r"([\w\.]*)\+?.*@[A-z]*.*\.com"

def exercise4():
    # 4. Matching HTML
    return r"<([a-z]*)"

def exercise5():
    # 5. Matching Specific Filenames
    return r"(\w+)\.(jpg|png|gif)$"
    # (.*)\.(jpg|png|gif)$

def exercise6():
    # 6. Trimming whitespace
    return r"^\s*(\S.*)$"
    # ^\s*([^\s]*.*)

def exercise7():
    # 7. Extracting information from a Log File
    return r"at\swidget\.List\.(\S*)\((.*):([0-9]+)\)"
    # return "\w*\.\w*.(\w*)\((.*.java):([0-9]*)"

def exercise8():
    # 8. Parsing and extracting data from a URL
    return r"^(\w*)://([\w\-\.]+)(:(\d+))?"
    # (\w*)://([\w\-]*(.com)?)(:([0-9]*))?