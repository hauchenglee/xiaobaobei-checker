import json
import re


class AIProcess:
    def __init__(self):
        pass

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
