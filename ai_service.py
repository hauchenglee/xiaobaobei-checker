import os

import anthropic
from poe_api_wrapper import PoeApi


class AIService:
    def __init__(self):
        self.prompt = '''
# 角色定义
你是繁体中文文本校对专家，专门检查错别字和错误文法（依据台湾教育部标准）。不检查语义与修辞。

# 核心检查规则
1. 用户自定义词库的优先匹配（`terms`参数中的词汇） 
2. 根据上下文检查同音异字错误（例：「平果」→「蘋果」）
2. 根据上下文检查常见混淆字（例：「原則尚」→「原則上」）
3. 根据上下文检查符号用法，中文符号使用全形「，」、「。」，但若表示为数字符号，则使用半形「,」、「.」。
  - 中文符号：这是第一句，每一句之间必须「，」，或者是「。」
  - 数字符号：但如果是15,000元，表示位数分位的「,」，或是3.1415，表示小数点「.」则依据数字符号用法

# 处理优先级
1. 先完成：优先匹配自定义词库。
  - 若文本中存在`terms`中的词汇，直接替换（即使单字正确）
2. 再检查：通用规则检查。
  - 未匹配`terms`时，应用形近/同音字修正

# 严格约束
- 输出必须符合JSON Schema定义
- 自定义词库优先于通用规则

# 输入输出规范

**输入JSON Schema**：
```json
{
  "type": "object",
  "properties": {
    "article": {"type": "string", "description": "待校对文本"},
    "terms": {"type": "array", "description": "优先匹配的自定义词库"}
  },
  "required": ["article", "terms"]
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
]
```

# 示例说明

**输入示例**：

```json
{
  "article": "该案件依第3階段办理，请参照事务管理手册第50点。如果您是平果公司的員工，可以申請育兒津鐵。",
  "terms": ["設籍並居住", "育兒津貼"]
}
```

**正确输出**：

```json
  {
  "corrected_text": "该案件依第3階段办理，请参照事务管理手册第五十点。如果您是蘋果公司的員工，可以申請育兒津貼。"
  }
```

当前输入内容：
'''

    def poe_service(self, data, bot):
        # poe api key generate: https://poe.com/api_key
        # https://github.com/snowby666/poe-api-wrapper
        # 初始化 PoeApi 客户端
        cookies = {
            'p-b': '8gRVN7ckMUHqu4bhRkmDwg%3D%3D',
            'p-lat': 'Zkpc9Nh9RFnorp05i46t9ARWjaKnmKGI%2BWYkPbpXgQ%3D%3D'
        }
        client = PoeApi(tokens=cookies)

        content = self.prompt + f"{data}"
        need_chat_code = True  # 是否要连续对话

        if need_chat_code:
            chat_code = None
            if chat_code:
                response_gen = client.send_message(bot, content, chatCode=chat_code)
            else:
                response_gen = client.send_message(bot, content)

            last_text = ""
            full_response = ""
            for chunk in response_gen:
                if 'chatCode' in chunk and not chat_code:
                    chat_code = chunk['chatCode']
                last_text = chunk["text"].lstrip()  # 只保存最後一個chunk的text

        else:
            response_gen = client.send_message(bot, content)

            last_text = ""
            full_response = ""
            for chunk in response_gen:
                last_text = chunk["text"].lstrip()  # 只保存最後一個chunk的text

        # 提取最後的JSON部分
        start_index = last_text.rfind('```json')
        end_index = last_text.rfind('```')
        if start_index != -1 and end_index != -1:
            json_text = last_text[start_index:end_index + 3]
            # 處理markdown code block
            json_text = json_text.replace('```json\n', '').replace('\n```', '')
            full_response = json_text

        return full_response

    def claude_service(self, data, bot):

        content = self.prompt + f"{data}"

        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        message = client.messages.create(
            model=bot,
            max_tokens=8192,
            messages=[
                {"role": "user", "content": content}
            ]
        )

        message = message.content[0].text

        return message
