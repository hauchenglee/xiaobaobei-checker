import json
import re


class AIProcess:
    def __init__(self):
        pass

    # 用语类别：代号(码)、国民身份证统一编号、编号、发文字号
    # 用法举例：
    # ISBN 988-133-005-1
    # M234567890
    # 附表(件)1
    # 院台秘字第0930086517号
    # 台79内字第095512号
    # 用语类别：序数
    # 用法举例：
    # 第4届第6会期
    # 第1阶段
    # 第1优先
    # 第2次
    # 第3名
    # 第4季
    # 第5会议室
    # 第6次会议纪录
    # 第7组
    # 用语类别：日期、时间
    # 用法舉例：
    # 民国93年7月8日
    # 93年度
    # 21世纪
    # 公元2000年
    # 7时50分
    # 挑战2008：国家发展重点计划
    # 520就职典礼
    # 72水灾
    # 921大地震
    # 911恐怖事件
    # 228事件
    # 38妇女节
    # 延后3周办理
    # 用语类别：电话、传真
    # 用法舉例：
    # (02)3356-6500
    # 用语类别：邮递区号、门牌号码
    # 用法舉例：
    # 100台北市中正区忠孝东路1段2号3楼304室
    # 用语类别：计量单位
    # 用法舉例：
    # 150公分
    # 35公斤
    # 30度
    # 2万元
    # 5角
    # 35立方公尺
    # 7.36公顷
    # 土地1.5笔
    # 用语类别：统计数据(如百分比、金额、人数、比数等)
    # 用法舉例：
    # 80%
    # 3.59%
    # 6亿3,944万2,789元
    # 639,442,789人
    # 1:3
    # 用语类别：法规条项款目、编章节款目之统计数据
    # 用法舉例：
    # 事务管理规则共分15编、415条条文
    # 用语类别：法规内容之引述或摘述
    # 用法舉例：
    # 依儿童福利法第44条规定：「违反第2条第2项规定者，处新台币1千元以上3万元以下罚锾。」
    # 儿童出生后10日内，接生人如未将出生之相关资料通报户政及卫生主管机关备查，依儿童福利法第44条规定，可处1千元以上、3万元以下罚锾。
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
        pattern_unit_cn = r"([零一二三四五六七八九十]+)(公尺|公分|公斤|斤|度|億|萬|千|百|元|筆|人|個|%)"
        if re.match(pattern_unit_cn, corrected_text):
            pass
        else:
            corrected_text = self.replace_to_arab(corrected_text)

        return corrected_text

    def replace_to_arab(self, corrected_text):
        chinese_to_arabic = {
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'
        }

        """将匹配的错误pattern替换为正确pattern"""
        corrected_text = ''.join([chinese_to_arabic[char] if char in chinese_to_arabic else char for char in corrected_text])
        return corrected_text

    def replace_to_cn(self, corrected_text):
        arabic_to_chinese = {
            '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
            '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
        }

        # 遍历字符串并替换阿拉伯数字为对应的中文数字
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
