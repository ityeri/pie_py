# From pie_py_old common_module/text_tasker.py
import hgtk

from . import utils


def replace_sangjamo(text: str) -> str:
    # 쌍자모를 전부 단자모로 만들고, ㅐㅔㅒㅖ 를 싸그리 ㅐ 로 바꿈
    text = utils.replace_double_jae(text)
    text = utils.replace_moe(text, 'ㅐㅔㅒㅖ', 'ㅐ')
    return text


def remove_special_char(text: str) -> str:
    # 특수문자, 공백, 줄바꿈 제거
    text = utils.multi_replace(text, '', "1234567890!@#$%^&*()`-=/\,.<>[]{};:")
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
        if hgtk.checker.is_hangul(char) and utils.is_complete_hangul(char):
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
    text = utils.multi_replace(text, '',
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