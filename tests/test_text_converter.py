from pie_py.censorship.core.text_converter import TextConverter
from pie_py.censorship.core.text_converter import convert_funcs

converter = TextConverter(
    [
        convert_funcs.replace_sangjamo,
        convert_funcs.remove_special_char,
        convert_funcs.filter_chosung_only,
        convert_funcs.filter_hangul_only,
        convert_funcs.filter_complete_hangul_only,
        convert_funcs.filter_alphabet_only,
        convert_funcs.to_lower_case,
        convert_funcs.remove_space_char
    ],
    3
)

for text in converter.get_converted_texts('씨1발'):
    print(text)