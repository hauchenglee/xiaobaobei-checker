import json


class AIProcess:
    def __init__(self):
        pass

    def find_differences(self, original_text, corrected_text):
        errors = []

        # 按句子分隔符将文本分割成句子
        def split_sentences(text):
            # 使用正则表达式分割句子，保留分隔符
            import re
            sentences = re.split('([。，])', text)
            # 将分隔符和句子组合
            combined = []
            for i in range(0, len(sentences) - 1, 2):
                combined.append(sentences[i] + sentences[i + 1])
            # 如果最后还有剩余文本(没有分隔符结尾)，也加入
            if len(sentences) % 2 == 1:
                combined.append(sentences[-1])
            return combined

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
        corrected_text = json.loads(message.content[0].text)['corrected_text']
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
