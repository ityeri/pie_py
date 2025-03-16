import hgtk
import hgtk.exception


def is_complete_hangul(char: str) -> bool:
    if len(char) != 1: raise hgtk.exception.NotLetterException

    if hgtk.checker.is_hangul(char):
        chosung, jungsung, _ = hgtk.letter.decompose(char)
        if chosung == '' or jungsung == '': return False
        else: return True

    else: raise hgtk.exception.NotHangulException


def replace_moe(text, oldMoe: str, newMoe: str):
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

def replace_double_jae(text):
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

def replace_double_moe(text):
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


def multi_replace(text: str, new: str, *olds: str):
    for oldPart in olds:
        if len(oldPart) == 1:
            old = oldPart
            text = text.replace(old, new)
        else:
            for old in oldPart:
                text = text.replace(old, new)

    return text



# 검열 코드에서 주로 사용되는 함수들
def replace_sangjamo(text: str) -> str:
    # 쌍자모를 전부 단자모로 만들고, ㅐㅔㅒㅖ 를 싸그리 ㅐ 로 바꿈
    text = replace_double_jae(text)
    text = replace_moe(text, 'ㅐㅔㅒㅖ', 'ㅐ')
    return text

def remove_special_char(text: str) -> str:
    # 특수문자, 공백, 줄바꿈 제거
    text = multi_replace(text, '', "1234567890!@#$%^&*()`-=/\,.<>[]{};:")
    text = remove_space_char(text)
    return text



def filter_chosung_only(text: str) -> str:
    # 초성만 남기고 한글이 아니거나, 모음만 있을경우는 무시
    result = str()

    for char in text:
        if hgtk.checker.is_hangul(char):
            chosung, jungsung, jongsung = hgtk.letter.decompose(char)

            # 완전한 한글 (애 아 엥 욍 등등) 일 경우
            if chosung != '' and jungsung != '':  # 종성 여부는 상관 없음
                result += chosung

            # 자음만 있을경우 (ㅁ ㄷ ㅃ ㄲ ㅋ)
            elif chosung != '' and jungsung == '':
                result += char

            # 모음만 있을경우 ㅔㅐㅏㅓㅣ
            elif chosung == '' and jungsung != '':
                continue

            # 종성만 있을경우 (ㄿ 같은 일부 문자는 종성에만 들어갈수 있음)
            elif chosung == '' and jungsung == '' and jongsung != '':
                result += char

    return result

def filter_hangul_only(text: str) -> str:
    # 한글 제외 다 제거 (불완전 한글 포함 ㅇ ㄷ ㅔ 등등)
    result = str()
    for char in text:
        if hgtk.checker.is_hangul(char):
            result += char

    return result

def filter_complete_hangul_only(text: str) -> str:
    # 한글 완전체 제외, 다 제거
    result = str()
    for char in text:
        if hgtk.checker.is_hangul(char) and is_complete_hangul(char):
            result += char

    return result

def filter_alphabet_only(text: str) -> str:
    # 영문 빼고 전부 제거
    result = str()
    for char in text:
        if text.lower() in 'abcdefghijklmnopqrstuvwxyz':
            result += char

    return result



def to_lower_case(text: str) -> str:
    return text.lower()

def remove_space_char(text: str) -> str:
    # 이상한 공백 문자, 줄바꿈 제거
    text = multi_replace(text, '',
                                    ' ', '\n', '	',
                                    '\u0020\u00a0'
                                    #  u+2000 ~ u+200f
                                    '\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007'
                                    '\u2008\u2009\u200a\u200b\u200c\u200d\u200e\u200f'
                                    # non space 문자
                                    '\u180e\u2800\u3164'
                                    # 기타
                                    '\u202f\u205f\u3000\u2060\ufeff')

    return text