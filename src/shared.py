def desanitize(string):
    mapped_chars = { 
        '__gt__': '>',
        '__lt__': '<',
        '__sq__': "'",
        '__dq__': '"',
        '__ob__': '[',
        '__cb__': ']',
        '__oc__': '{',
        '__cc__': '}',
        '__at__': '@',
        '__cn__': '\n',
        '__cr__': '\r',
        '__tc__': '\t',
        '__pd__': '#'}

    for key in mapped_chars.keys():
        string = string.replace(key, mapped_chars[key])

    return string