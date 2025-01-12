import hgtk
import hgtk.exception


def isCompleteHangul(char: str) -> bool:
    if len(char) != 1: raise hgtk.exception.NotLetterException

    if hgtk.checker.is_hangul(char):
        chosung, jungsung, _ = hgtk.letter.decompose(char)
        if chosung == '' or jungsung == '': return False
        else: return True

    else: hgtk.exception.NotHangulException


def replaceMoe(text, oldMoe: str, newMoe: str):
    # ㅐㅒㅔㅖ 전부 통일하는거

    result = ''

    for char in text:
        if hgtk.checker.is_hangul(char):

            chosung, jungsung, jongsung = hgtk.letter.decompose(char)

            # 완전한 한글 (애 아 엥 욍 등등) 일 경우
            if chosung != '' and jungsung != '': # 종성 여부는 상관 없음
                if jungsung in oldMoe: jungsung = newMoe
                result += hgtk.letter.compose(chosung, jungsung, jongsung)

            # 자음만 있을경우 (ㅁ ㄷ ㅃ ㄲ ㅋ)
            elif chosung != '' and jungsung == '':
                result += char

            # 모음만 있을경우 ㅔㅐㅏㅓㅣ
            elif chosung == '' and jungsung != '':
                if jungsung in oldMoe: jungsung = newMoe
                result += jungsung

            # 종성만 있을경우 (ㄿ 같은 일부 문자는 종성에만 들어갈수 있음)
            elif chosung == '' and jungsung == '' and jongsung != '':
                result += char

        else:
            result += char  # 한글이 아니면 그대로 추가
    
    return result

def replaceDoubleJae(text):
    # 쌍자음을 단자음으로 매핑
    doubleJaeTable = {
        'ㄲ': 'ㄱ', 
        'ㄳ': 'ㄱ',

        'ㄵ': 'ㄴ',
        'ㄶ': 'ㄴ',

        'ㄸ': 'ㄷ', 

        'ㄺ': 'ㄹ',
        'ㄻ': 'ㄹ',
        'ㄼ': 'ㄹ',
        'ㄽ': 'ㄹ',
        'ㄾ': 'ㄹ',
        'ㄿ': 'ㄹ',
        'ㅀ': 'ㄹ',


        'ㅃ': 'ㅂ', 
        'ㅄ': 'ㅂ',

        'ㅆ': 'ㅅ', 
        'ㅉ': 'ㅈ'
    }
    
    result = ''

    for char in text:
        if hgtk.checker.is_hangul(char):

            chosung, jungsung, jongsung = hgtk.letter.decompose(char)

            # 완전한 한글 (애 아 엥 욍 등등) 일 경우
            if chosung != '' and jungsung != '': # 종성 여부는 상관 없음
                # 쌍자음인 경우 단자음으로 변경
                if chosung in doubleJaeTable: chosung = doubleJaeTable[chosung]
                if jongsung in doubleJaeTable: jongsung = doubleJaeTable[jongsung]
                result += hgtk.letter.compose(chosung, jungsung, jongsung)
            
            # 자음만 있을경우 (ㅁ ㄷ ㅃ ㄲ ㅋ)
            elif chosung != '' and jungsung == '':
                if chosung in doubleJaeTable: chosung = doubleJaeTable[chosung]
                result += chosung

            # 모음만 있을경우 ㅔㅐㅏㅓㅣ
            elif chosung == '' and jungsung != '':
                result += char

            # 종성만 있을경우 (ㄿ 같은 일부 문자는 종성에만 들어갈수 있음)
            elif chosung == '' and jungsung == '' and jongsung != '':
                if jongsung in doubleJaeTable: jongsung = doubleJaeTable[jongsung]
                result += jongsung
            
        else:
            result += char  # 한글이 아니면 그대로 추가
    
    return result

def replaceDoubleMoe(text):
    # 쌍모음을 단모음으로
    doubleMoeTable = {
        'ㅒ': 'ㅐ',
        'ㅖ': 'ㅔ',
        'ㅛ': 'ㅗ',
        'ㅠ': 'ㅜ'
    }
    
    result = ''

    for char in text:
        if hgtk.checker.is_hangul(char):

            chosung, jungsung, jongsung = hgtk.letter.decompose(char)

            # 완전한 한글 (애 아 엥 욍 등등) 일 경우
            if chosung != '' and jungsung != '': # 종성 여부는 상관 없음
                # 쌍모음인 경우 단모음 으로
                if jungsung in doubleMoeTable: jungsung = doubleMoeTable[jungsung]
                result += hgtk.letter.compose(chosung, jungsung, jongsung)
            
            # 자음만 있을경우 (ㅁ ㄷ ㅃ ㄲ ㅋ)
            elif chosung == '' and jungsung != '':
                result += char

            # 모음만 있을경우 (ㅁ ㄷ ㅃ ㄲ ㅋ)
            elif chosung != '' and jungsung == '':
                # 쌍모음인 경우 단모음 으로
                if jungsung in doubleMoeTable: jungsung = doubleMoeTable[jungsung]
                result += hgtk.letter.compose(chosung, jungsung, jongsung)

            # 종성만 있을경우 (일부 자음은 종성에만 들어갈수 있)
            elif chosung == '' and jungsung == '' and jongsung != '':
                result += char
            
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
