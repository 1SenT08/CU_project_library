def filter_punctuation(word):
    punctuation_list = [',', '.', '?', '!', ':', ';',
                        '\'', '"', '...', '-', '(', ')',
                        '[', ']', '{', '}', '%', '$', '#',
                        '@', '=', '+', '&', " ", "№"]
    
    for item in punctuation_list:
        if item in word:
            return False
    
    return True


def pretext(word):
    pretext_list = ["в", "к", "с", "на", "по", "о", "до", "за", 
                    "об", "у", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
    return not (word.lower() in pretext_list)