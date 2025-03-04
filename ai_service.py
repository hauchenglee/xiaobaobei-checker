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
4. 数字使用原则：
  - [阿拉伯数字适用]
    - 代号类：身份证编号/ISBN/公文字号等
    - 序数词：第4届/第3名/第7组等
    - 时间日期：93年度/7时50分/228事件等
    - 联络信息：(02)3356-6500/100台北市忠孝东路1段2号
    - 计量单位：150公分/2万元/7.36公顷
    - 统计数据：80%/6亿3,944万2,789元/1:3
    - 法规引用：儿童福利法第44条/处1千元以上
  - [中文数字适用]
    - 描述性用语：三大面向/每一位同仁/一套规范
    - 专有名词：五南书局/三国演义/九九峰
    - 惯用表达：星期一/约三、四天/七千余人
    - 法制作业：第一百十一条/第五十一点/计五十一条

# 处理优先级

1. 优先匹配自定义词库：若文本中存在`terms`中的词汇，直接替换（即使单字正确）
2. 应用数字使用原则：数字转换需同时符合：①类别归属正确 ②格式规范（如千分位、单位间距）
3. 通用规则检查：未匹配`terms`时，应用形近/同音字修正

# 严格约束

- 仅输出JSON格式，禁用Markdown
- 错误必须符合Schema定义
- 自定义词库优先于数字使用原则与通用规则

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
  "terms": ["設籍並居住", "育兒津貼"],
  "is_ai": true
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
            json_text = last_text[start_index:end_index+3]
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
