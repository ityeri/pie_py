# From pie_py_old common_module/text_tasker.py
import hgtk


def is_complete_hangul(char: str) -> bool:
    if len(char) != 1: raise ValueError

    if hgtk.checker.is_hangul(char):
        chosung, jungsung, _ = hgtk.letter.decompose(char)
        if chosung == '' or jungsung == '':
            return False
        else:
            return True

    else:
        raise ValueError

def replace_moe(text, old_moe: str, new_moe: str):
    # ㅐㅒㅔㅖ 전부 통일하는거

    result = ''

    for char in text:
        if hgtk.checker.is_hangul(char):

            chosung, jungsung, jongsung = hgtk.letter.decompose(char)

            # 완전한 한글 (애 아 엥 욍 등등) 일 경우
            if chosung != '' and jungsung != '':  # 종성 여부는 상관 없음
                if jungsung in old_moe: jungsung = new_moe
                result += hgtk.letter.compose(chosung, jungsung, jongsung)

            # 자음만 있을경우 (ㅁ ㄷ ㅃ ㄲ ㅋ)
            elif chosung != '' and jungsung == '':
                result += char

            # 모음만 있을경우 ㅔㅐㅏㅓㅣ
            elif chosung == '' and jungsung != '':
                if jungsung in old_moe: jungsung = new_moe
                result += jungsung

            # 종성만 있을경우 (ㄿ 같은 일부 문자는 종성에만 들어갈수 있음)
            elif chosung == '' and jungsung == '' and jongsung != '':
                result += char

        else:
            result += char  # 한글이 아니면 그대로 추가

    return result

def replace_double_jae(text):
    # 쌍자음을 단자음으로 매핑
    double_jae_table = {
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
            if chosung != '' and jungsung != '':  # 종성 여부는 상관 없음
                # 쌍자음인 경우 단자음으로 변경
                if chosung in double_jae_table: chosung = double_jae_table[chosung]
                if jongsung in double_jae_table: jongsung = double_jae_table[jongsung]
                result += hgtk.letter.compose(chosung, jungsung, jongsung)

            # 자음만 있을경우 (ㅁ ㄷ ㅃ ㄲ ㅋ)
            elif chosung != '' and jungsung == '':
                if chosung in double_jae_table: chosung = double_jae_table[chosung]
                result += chosung

            # 모음만 있을경우 ㅔㅐㅏㅓㅣ
            elif chosung == '' and jungsung != '':
                result += char

            # 종성만 있을경우 (ㄿ 같은 일부 문자는 종성에만 들어갈수 있음)
            elif chosung == '' and jungsung == '' and jongsung != '':
                if jongsung in double_jae_table: jongsung = double_jae_table[jongsung]
                result += jongsung

        else:
            result += char  # 한글이 아니면 그대로 추가

    return result

def multi_replace(text: str, new: str, *olds: str):
    for old_part in olds:
        if len(old_part) == 1:
            old = old_part
            text = text.replace(old, new)
        else:
            for old in old_part:
                text = text.replace(old, new)

    return text