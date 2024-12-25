import hgtk

def replaceJae(text):
    result = ''
    for char in text:
        if hgtk.checker.is_hangul(char):
            try:
                chosung, jungsung, jongsung = hgtk.letter.decompose(char)

                # print(f'"{chosung}" "{jungsung}" "{jongsung}"')
                
                # 글자가 ㄱ ㅋㅋ ㅇㅇ 과 같이 자음만 있으면
                if jungsung == '' and jongsung == '':
                    result += char
                    continue
                # 글자가 ㅏ ㅣ ㅙ ㅒ 같이 모음만 있으면
                elif chosung == '' and jongsung == '':
                    result += char
                    continue

                # ㅔ -> ㅐ, ㅖ -> ㅒ
                if jungsung == 'ㅔ':
                    jungsung = 'ㅐ'
                elif jungsung == 'ㅖ':
                    jungsung = 'ㅐ'
                elif jungsung == 'ㅒ':
                    jungsung = 'ㅐ'

                result += hgtk.letter.compose(chosung, jungsung, jongsung)
            except: result += char
        else:
            result += char  # 한글이 아니면 그대로 추가
    
    return result

def replaceDoubleJae(text):
    # 쌍자음을 단자음으로 매핑
    double_consonants = {
        'ㄲ': 'ㄱ', 'ㄸ': 'ㄷ', 'ㅃ': 'ㅂ', 'ㅆ': 'ㅅ', 'ㅉ': 'ㅈ'
    }
    
    result = ''
    for char in text:
        if hgtk.checker.is_hangul(char):
            try:
                chosung, jungsung, jongsung = hgtk.letter.decompose(char)

                if jungsung == '' and jongsung == '':
                    result += char
                    continue
                
                # 쌍자음인 경우 단자음으로 변경
                if chosung in double_consonants:
                    chosung = double_consonants[chosung]
                
                result += hgtk.letter.compose(chosung, jungsung, jongsung)
            except: result += char
        else:
            result += char  # 한글이 아니면 그대로 추가
    
    return result

def multiReplace(text: str, new: str, *olds: str):
    for oldPart in olds:
        if len(oldPart) == 1:
            old = oldPart
            text = text.replace(old, new)
        else:
            for old in oldPart:
                text = text.replace(old, new)

    return text
