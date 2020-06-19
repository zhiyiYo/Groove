import re

def autoWrap(text:str,maxCharactersNum:int):
    """ 根据专辑名的长度决定是否换行 """
    # 设置换行标志位
    isWordWrap = True
    text_list = list(text)
    alpha_num = 0
    not_alpha_num = 0
    blank_index = 0
    for index, i in enumerate(text):
        Match = re.match(r'[A-Z0-9a-z\(\)\*\.\s]', i)
        if Match:
            alpha_num += 1
            if Match.group() == ' ':
                # 记录上一个空格的下标
                blank_index = index
            if alpha_num + 2 * not_alpha_num == maxCharactersNum:
                # 发生异常就说明正好22个长度
                try:
                    if text[index + 1] == ' ':
                        # 插入换行符
                        text_list.insert(index + 1, '\n')
                        # 弹出空格
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
    
    return newText,isWordWrap
    
