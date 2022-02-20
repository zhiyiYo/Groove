# coding: utf-8
import re


def autoWrap(text: str, maxCharactersNum: int) -> tuple:
    """ auto word wrap according to the length of the string

    Parameters
    ----------
    maxCharactersNum: int
        the length of text (convert to letter size, e.g. `你.length = 2`)

    Returns
    -------
    newText: str
        text after auto word wrap process

    isWordWrap: bool
        whether a line break occurs in the text
    """
    isWordWrap = True
    text_list = list(text)
    alpha_num = 0
    not_alpha_num = 0
    blank_index = 0
    for index, i in enumerate(text):
        Match = re.match(r'[0-9A-Za-z:\+\-\{\}\d\(\)\*\.\s]', i)
        if Match:
            alpha_num += 1
            if Match.group() == ' ':
                # record previous blank position
                blank_index = index

            if alpha_num + 2 * not_alpha_num == maxCharactersNum:
                try:
                    if text[index + 1] == ' ':
                        # insert \n
                        text_list.insert(index + 1, '\n')
                        # pop blank
                        text_list.pop(index + 2)
                    else:
                        text_list.insert(blank_index, '\n')
                        text_list.pop(blank_index + 1)
                    break
                except IndexError:
                    pass

        else:
            not_alpha_num += 1
            if alpha_num + 2 * not_alpha_num == maxCharactersNum:
                text_list.insert(index + 1, '\n')
                try:
                    if text_list[index + 2] == ' ':
                        text_list.pop(index + 2)
                    break
                except:
                    pass
            elif alpha_num + 2 * not_alpha_num > maxCharactersNum:
                if text_list[index - 1] == ' ':
                    text_list.insert(index - 1, '\n')
                    text_list.pop(index)
                else:
                    text_list.insert(index, '\n')
                break
    else:
        isWordWrap = False

    newText = ''.join(text_list)

    return newText, isWordWrap
