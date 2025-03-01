import os
import anthropic
from poe_api_wrapper import PoeApi


class AIService:
    def __init__(self):
        self.prompt = '''
# 角色定义
你是繁体中文文本校对专家，专门检查错别字和错误文法与语义（依据台湾教育部标准）。

# 核心检查规则
**需检查**：
1. 同音异字错误（例：「平果」→「蘋果」）
2. 常见混淆字（例：「原則尚」→「原則上」）
3. 用户自定义词库的优先匹配（`terms`参数中的词汇）

# 处理优先级

1. **优先匹配自定义词库**：若文本中存在`terms`中的词汇，直接替换（即使单字正确）
2. **通用规则检查**：未匹配`terms`时，应用形近/同音字修正

# 严格约束

- 仅输出JSON格式，禁用Markdown
- 错误必须符合Schema定义
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

当前输入内容：
'''

    def poe_service(self, data, bot):
        # poe api key generate: https://poe.com/api_key
        # https://github.com/snowby666/poe-api-wrapper
        # 初始化 PoeApi 客户端
        cookies = {
            'p-b': os.environ.get("POE_COOKIE_P_B"),
            'p-lat': os.environ.get("POE_COOKIE_P_LAT")
        }
        client = PoeApi(tokens=cookies)

        content = self.prompt + f"{data}"
        need_chat_code = False  # 是否要连续对话

        if need_chat_code:
            chat_code = None
            if chat_code:
                response_gen = client.send_message(bot, content, chatCode=chat_code)
            else:
                response_gen = client.send_message(bot, content)

            full_response = ""
            for chunk in response_gen:
                if 'chatCode' in chunk and not chat_code:
                    chat_code = chunk['chatCode']
                    full_response += chunk["response"].lstrip()
        else:
            response_gen = client.send_message(bot, content)

            full_response = ""
            for chunk in response_gen:
                full_response += chunk["response"].lstrip()

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

        return message
