import re
import pycorrector
import torch
import kenlm
from autocorrect import Speller
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class CheckService:
    def __init__(self):
        self.spell = Speller(lang='en')
        self.cn_corrector = pycorrector.Corrector()
        self.en_corrector = pycorrector.EnSpellCorrector()
        # 增加 debug 输出
        print("Pycorrector version:", pycorrector.__version__)

    def check_chinese(self, text):
        try:
            errors = []

            # 繁体转简体
            text = pycorrector.traditional2simplified(text)

            # 使用 pycorrector 进行检查
            results = self.cn_corrector.correct(text)
            # 处理返回的错误信息
            if isinstance(results, dict) and 'errors' in results:
                for error in results['errors']:
                    # error 格式为 (wrong, right, position)
                    if len(error) >= 3:
                        wrong, right, pos = error
                        errors.append({
                            'original': wrong,
                            'correction': right,
                            'type': 'chinese_correction',
                            'position': pos
                        })

            return errors

        except Exception as e:
            print(f"Error in Chinese correction: {str(e)}")
            return []

    def check_terms(self, text, terms):
        errors = []

        # 将词条按长度降序排序，确保优先匹配较长的词条
        sorted_terms = sorted(terms, key=len, reverse=True)

        for term in sorted_terms:
            # 在文本中查找近似匹配
            for i in range(len(text)):
                if i + len(term) > len(text):
                    break

                text_slice = text[i:i + len(term)]
                if text_slice != term:
                    # 计算编辑距离或相似度
                    similar = False
                    diff_count = sum(1 for a, b in zip(text_slice, term) if a != b)

                    # 如果长度相同且只有一个字符不同，认为是可能的错误
                    if len(text_slice) == len(term) and diff_count == 1:
                        similar = True

                    if similar:
                        errors.append({
                            'original': text_slice,
                            'correction': term,
                            'type': 'term_mismatch',
                            'position': i
                        })

        return errors

    def process_data(self, data):
        article = data.get('article', '')
        terms = data.get('terms', [])

        if not article:
            return {
                "status": "error",
                "message": "文章内容不能为空",
                "errors": []
            }

        all_errors = []
        print("Processing data...")

        # 1. 先进行术语检查
        term_errors = []  # 先初始化
        if terms:
            term_errors = self.check_terms(article, terms)
            all_errors.extend(term_errors)

        # 2. 创建术语检查已覆盖的位置范围
        covered_ranges = []
        for error in term_errors:
            pos = error['position']
            length = len(error['original'])
            covered_ranges.append((pos, pos + length))

        # 3. 中文错别字检查，但跳过已被术语检查覆盖的部分
        chinese_errors = self.check_chinese(article)
        for error in chinese_errors:
            pos = error['position']
            length = len(error['original'])

            # 检查这个位置是否已被术语检查覆盖
            is_covered = False
            for start, end in covered_ranges:
                if pos >= start and pos < end:
                    is_covered = True
                    break

            if not is_covered:
                all_errors.append(error)

        # 按位置排序错误
        all_errors.sort(key=lambda x: x['position'])

        # 生成修正后的文本
        corrected_text = article
        if all_errors:
            # 从后向前替换，避免位置偏移
            for error in reversed(all_errors):
                pos = error['position']
                original = error['original']
                correction = error['correction']
                corrected_text = (
                        corrected_text[:pos] +
                        correction +
                        corrected_text[pos + len(original):]
                )

        # 繁体转简体
        corrected_text = pycorrector.simplified2traditional(corrected_text)

        result = {
            "status": "success",
            "message": "检查完成",
            "original_text": article,
            "corrected_text": corrected_text,
            "errors": [
                {
                    "type": error['type'],
                    "original": error['original'],
                    "correction": error['correction'],
                    "position": error['position']
                } for error in all_errors
            ]
        }

        return result
