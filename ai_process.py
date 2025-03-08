import json
import re


class AIProcess:
    def __init__(self):
        pass

    def check_number(self, corrected_text):
        pattern_arab_number = r"[1-9]"
        pattern_cn_number = r"[一二三四五六七八九]"

        # Arab第一种：编号
        pattern_human_id_cn = r"^[A-Z][零一二三四五六七八九十]{9}$"
        if re.match(pattern_human_id_cn, corrected_text):
            corrected_text = self.replace_to_arab(corrected_text)

        # Arab第二种：序数
        pattern_ordinal_cn = r"第[零一二三四五六七八九十]+"
        if re.match(pattern_ordinal_cn, corrected_text):
            pass
        else:
            corrected_text = self.replace_to_arab(corrected_text)

        # 第三种：日期、时间
        pattern_datetime_cn = r"([零一二三四五六七八九十]+)(年|月|日|世紀|世纪|時|时|分|秒|週)"
        if re.match(pattern_datetime_cn, corrected_text):
            pass
        else:
            corrected_text = self.replace_to_arab(corrected_text)

        # 第四种：电话

        # 第五种：地址
        pattern_address_cn = r"([零一二三四五六七八九十]+)樓"
        if re.match(pattern_address_cn, corrected_text):
            pass
        else:
            corrected_text = self.replace_to_arab(corrected_text)

        # 第六种：计量单位
        pattern_unit_cn = r"([零一二三四五六七八九十]+)(公尺|公分|公斤|斤|度|億|萬|千|百|元|筆|個|%)"
        if re.match(pattern_unit_cn, corrected_text):
            pass
        else:
            corrected_text = self.replace_to_arab(corrected_text)

        # 转换中文
        # 针对 星期、週和初 的规则
        # 星期一~星期六
        pattern_weekday_cn = r"星期[1-6]"
        # 週一~週六
        pattern_zhounum_cn = r"週[1-6]"
        # 初一到初六
        pattern_chu_cn = r"初[1-6]"

        # 如果匹配到规则，将数字转换为中文
        if re.search(pattern_weekday_cn, corrected_text):
            corrected_text = re.sub(r"星期([1-6])", lambda m: f"星期{self.replace_to_cn(m.group(1))}", corrected_text)
        elif re.search(pattern_zhounum_cn, corrected_text):
            corrected_text = re.sub(r"週([1-6])", lambda m: f"週{self.replace_to_cn(m.group(1))}", corrected_text)
        elif re.search(pattern_chu_cn, corrected_text):
            corrected_text = re.sub(r"初([1-6])", lambda m: f"初{self.replace_to_cn(m.group(1))}", corrected_text)

        return corrected_text

    def replace_to_arab(self, corrected_text):
        chinese_to_arabic = {
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'
        }

        corrected_text = ''.join([chinese_to_arabic[char] if char in chinese_to_arabic else char for char in corrected_text])
        return corrected_text

    def replace_to_cn(self, corrected_text):
        arabic_to_chinese = {
            '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
            '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
        }

        corrected_text = ''.join([arabic_to_chinese[char] if char in arabic_to_chinese else char for char in corrected_text])
        return corrected_text

    def find_differences(self, original_text, corrected_text):
        errors = []

        # 按句子分隔符将文本分割成句子
        def split_sentences(text):
            # 使用正则表达式查找句子和标点
            sentence_parts = []
            current_pos = 0

            # 查找所有标点符号（句号或逗号）
            punctuation_positions = []
            for match in re.finditer('[。，]', text):
                punctuation_positions.append((match.start(), match.group()))

            if not punctuation_positions:
                # 如果没有找到标点符号，则整个文本作为一个句子
                return [text]

            # 处理连续标点符号
            i = 0
            while i < len(punctuation_positions):
                # 查找连续标点的结束位置
                j = i
                while j + 1 < len(punctuation_positions) and punctuation_positions[j + 1][0] == punctuation_positions[j][0] + 1:
                    j += 1

                # 获取最后一个标点的位置及其符号
                end_pos, end_punct = punctuation_positions[j]

                # 添加从当前位置到标点符号的句子
                sentence = text[current_pos:end_pos + 1]  # 包含标点符号
                if sentence:
                    sentence_parts.append(sentence)

                # 更新当前位置
                current_pos = end_pos + 1
                i = j + 1

            # 添加最后一个句子（如果有）
            if current_pos < len(text):
                sentence_parts.append(text[current_pos:])

            return sentence_parts

        # 分割原文和修正后的文本
        original_sentences = split_sentences(original_text)
        corrected_sentences = split_sentences(corrected_text)

        # 确保两个文本的句子数量相同
        min_len = min(len(original_sentences), len(corrected_sentences))

        # 逐句比对
        for i in range(min_len):
            if original_sentences[i] != corrected_sentences[i]:
                errors.append({
                    'original': original_sentences[i],
                    'correction': corrected_sentences[i]
                })

        return errors

    def process_data(self, article, message):
        response = str(message)
        corrected_text = json.loads(message)['corrected_text']
        corrected_text = self.check_number(corrected_text)
        all_errors = self.find_differences(article.replace(",", "，"), corrected_text.replace(",", "，"))
        result = {
            "status": "success",
            "message": "检查完成",
            "response": response,
            "original_text": article,
            "corrected_text": corrected_text,
            "errors": [
                {
                    "original": error['original'],
                    "correction": error['correction']
                } for error in all_errors
            ]
        }

        return result
