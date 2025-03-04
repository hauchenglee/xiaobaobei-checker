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
**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：代号(码)、国民身份证统一编号、编号、发文字号
**用法举例**：
- ISBN 988-133-005-1
- M234567890
- 附表(件)1
- 院台秘字第0930086517号
- 台79内字第095512号

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：序数
**用法举例**：
- 第4届第6会期
- 第1阶段
- 第1优先
- 第2次
- 第3名
- 第4季
- 第5会议室
- 第6次会议纪录
- 第7组

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：日期、时间
**用法举例**：
- 民国93年7月8日
- 93年度
- 21世纪
- 公元2000年
- 7时50分
- 挑战2008：国家发展重点计划
- 520就职典礼
- 72水灾
- 921大地震
- 911恐怖事件
- 228事件
- 38妇女节
- 延后3周办理

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：电话、传真
**用法举例**：
- (02)3356-6500

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：邮递区号、门牌号码
**用法举例**：
- 100台北市中正区忠孝东路1段2号3楼304室

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：计量单位
**用法举例**：
- 150公分
- 35公斤
- 30度
- 2万元
- 5角
- 35立方公尺
- 7.36公顷
- 土地1.5笔

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：统计数据(如百分比、金额、人数、比数等)
**用法举例**：
- 80%
- 3.59%
- 6亿3,944万2,789元
- 639,442,789人
- 1:3

**阿拉伯数字/中文数字**：中文数字
**用语类别**：描述性用语
**用法举例**：
- 一律、一致性
- 再一次、一再强调
- 一流大学
- 前一年
- 一分子
- 三大面向
- 四大施政主轴
- 一次补助
- 一个多元族群的社会
- 每一位同仁
- 一支部队
- 一套规范
- 不二法门
- 三生有幸
- 新十大建设
- 国土三法
- 组织四法
- 零岁教育
- 核四厂
- 第一线上
- 第二专长
- 第三部门
- 公正第三人
- 第一夫人
- 三级制政府
- 国小三年级

**阿拉伯数字/中文数字**：中文数字
**用语类别**：专有名词(如地名、书名、人名、店名、头衔等)
**用法举例**：
- 九九峰
- 三国演义
- 李四
- 五南书局
- 恩史瓦第三世

**阿拉伯数字/中文数字**：中文数字
**用语类别**：惯用语（如星期、比例、概数、约数）
**用法举例**：
- 星期一
- 週一
- 正月初五
- 十分之一
- 三读
- 三军部队
- 约三、四天
- 二三百架次
- 几十万分之一
- 七千余人
- 二百多人

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：法规条项款目、编章节款目之统计数据
**用法举例**：
- 事务管理规则共分15编、415条条文

**阿拉伯数字/中文数字**：阿拉伯数字
**用语类别**：法规内容之引述或摘述
**用法举例**：
- 依儿童福利法第44条规定：「违反第2条第2项规定者，处新台币1千元以上3万元以下罚锾。」
- 儿童出生后10日内，接生人如未将出生之相关资料通报户政及卫生主管机关备查，依儿童福利法第44条规定，可处1千元以上、3万元以下罚锾。

**阿拉伯数字/中文数字**：中文数字
**用语类别**：法规制订、修正及废止案之法制作业公文书（如令、函、法规草案总说明、条文对照表等）
**用法举例**：
- 行政院令：修正「事务管理规则」第一百十一条条文。
- 行政院函：修正「事务管理手册」财产管理第五十点、第五十一点、第五十二点，并自中华民国九十三年二月十六日生效...。
- 「○○法」草案总说明：...爰拟具「○○法」草案，计五十一条。
- 关税法施行细则部分条文修正草案条文对照表之「说明」栏－修正条文第十六条之说明：一、关税法第十二条第一项计算关税完税价格附加比例已减低为百分之五，本条第一项爰予配合修正。

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
