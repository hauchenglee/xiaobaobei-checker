import re
import pycorrector
import torch
import kenlm
from autocorrect import Speller
import ssl
import os
import json
import anthropic
from poe_api_wrapper import PoeApi

ssl._create_default_https_context = ssl._create_unverified_context


class CheckService:
    def __init__(self):
        # https://deepspeech.bj.bcebos.com/zh_lm/zh_giga.no_cna_cmn.prune01244.klm 下载了
        # self.klm_path = './models/zh_giga.no_cna_cmn.prune01244.klm'
        self.klm_path = '/opt/models/zh_giga.no_cna_cmn.prune01244.klm'

        if not os.path.exists(self.klm_path):
            raise RuntimeError(f"Model file not found at: {self.klm_path}")

        try:
            self.cn_corrector = pycorrector.Corrector(language_model_path=self.klm_path)
            self.spell = Speller(lang='en')
            self.en_corrector = pycorrector.EnSpellCorrector()
            print(f"Successfully initialized Chinese corrector with model at {self.klm_path}")
        except Exception as e:
            print(f"Error initializing Chinese corrector: {str(e)}")
            raise

        # 增加 debug 输出
        print("Pycorrector version:", pycorrector.__version__)

        self.prompt = '''
# 角色定义
你是繁体中文文本校对专家，专门检查错别字和错误用字（依据台湾教育部标准）。

# 核心检查规则
**需检查**：
1. 同音异字错误（例：「平果」→「蘋果」）
2. 常见混淆字（例：「原則尚」→「原則上」）
3. 用户自定义词库的优先匹配（`terms`参数中的词汇）

**不检查**：
- 语法结构
- 语义合理性
- 标点符号
- 表达风格

# 修正規則
- 每個錯誤修正必須保持原字數不變
- 示例：
  輸入：「如果您是平果公司」
  輸出：「如果您是蘋果公司」

# 输入输出规范
**输入JSON Schema**：
```json
{
  "type": "object",
  "properties": {
    "article": {"type": "string", "description": "待校对文本（必须为繁体中文）"},
    "terms": {"type": "array", "items": {"type": "string"}, "description": "优先匹配的自定义词库"},
    "is_ai": {"type": "boolean", "description": "系统保留参数"}
  },
  "required": ["article", "terms", "is_ai"]
}
```

**输出JSON Schema**：

```json
{
  "type": "object",
  "properties": {
    "corrected_text": {
      "type": "string",
      "description": "修正之后的语句"
    },
    "additionalProperties": false
  },
  "required": ["corrected_text"]
}
```

# 处理优先级

1. **优先匹配自定义词库**：若文本中存在`terms`中的词汇，直接替换（即使单字正确）
2. **通用规则检查**：未匹配`terms`时，应用形近/同音字修正

# 示例说明

**输入示例**：

```json
{
  "article": "如果您是平果公司的員工，可以申請育兒津鐵。",
  "terms": ["設籍並居住", "育兒津貼"],
  "is_ai": true
}
```

**正确输出**：

```json
{
  "corrected_text": "如果您是蘋果公司的員工，可以申請育兒津貼。"
}
```

# 严格约束

- 仅输出JSON格式，禁用Markdown
- 错误必须符合Schema定义
- 自定义词库优先于通用规则
- 自定义词库中的词组必须与原文保持相同字数

当前输入内容：
'''

    def poe_service(self, data):
        # poe api key generate: https://poe.com/api_key
        # 初始化 PoeApi 客户端
        token = ""
        client = PoeApi(token)
        bot = "Claude-3.5-Sonnet-200k"

        content = self.prompt + f"{data}"
        response_gen = client.send_message(bot, content)

        full_response = ""
        for chunk in response_gen:
            full_response += chunk["response"].lstrip()

        print(full_response)

        return full_response

    def claude_service(self, data):

        content = self.prompt + f"{data}"

        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": content}
            ]
        )

        print("ANTHROPIC_API_KEY: " + os.environ.get("ANTHROPIC_API_KEY"))
        print("claude-3-5-sonnet-20240620 message: ")
        print(message)

        # 解析JSON
        data = json.loads(message.content[0].text)

        # 提取corrected_text列表
        corrected_text = data['corrected_text']
        print("corrected_text: ")
        print(corrected_text)

        return corrected_text

    def find_differences(self, original_text, corrected_text):
        errors = []
        i = 0
        while i < len(original_text) and i < len(corrected_text):
            if original_text[i] != corrected_text[i]:
                errors.append({
                    "original": original_text[i],
                    "correction": corrected_text[i],
                    "position": i
                })
            i += 1
        return errors

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
                        # 都转换成繁体保持一致
                        wrong = pycorrector.simplified2traditional(wrong)
                        right = pycorrector.simplified2traditional(right)
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
        print(data)
        article = data.get('article', '')
        terms = data.get('terms', [])
        is_ai = data.get('is_ai', False)
        print(f"is_ai: {is_ai}")

        if not article:
            return {
                "status": "error",
                "message": "文章内容不能为空",
                "errors": []
            }

        all_errors = []
        print("Processing data...")

        if is_ai:
            print("AI mode")
            corrected_text = self.poe_service(data)
            all_errors = self.find_differences(article, corrected_text)

            result = {
                "status": "success",
                "message": "检查完成",
                "original_text": article,
                "corrected_text": corrected_text,  # 直接使用 AI 返回的 corrected_text
                "errors": [
                    {
                        "original": error['original'],
                        "correction": error['correction'],
                        "position": error['position']
                    } for error in all_errors
                ]
            }
        else:
            print("Human mode")
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

            # 简体转繁体
            corrected_text = pycorrector.simplified2traditional(corrected_text)

            result = {
                "status": "success",
                "message": "检查完成",
                "original_text": article,
                "corrected_text": corrected_text,
                "errors": [
                    {
                        "original": error['original'],
                        "correction": error['correction'],
                        "position": error['position']
                    } for error in all_errors
                ]
            }

        return result
