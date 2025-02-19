# 使用 SpellChecker + re + pycorrector 作为基本的中文与英文错别字文字检查
# 进阶功能，加上List, Dict + re作为上下文语义检查

class CheckService:
    def process_data(self, data):
        article = data.get('article', '')
        terms = data.get('terms', [])
        is_context = data.get('is_context', False)

        # {
        #    "article":"身心障礙者生活補助",
        #    "terms":[
        #       "低收入戶",
        #       "中低收入戶",
        #       "身心障礙證明",
        #       "身心障礙者生活補助",
        #       "育兒津貼",
        #       "托育補助",
        #       "人籍合一",
        #       "設籍並居住"
        #    ],
        #    "is_context":false
        # }

        # 这里放你的业务逻辑
        result = {
            "message": "Processed by CheckService",
            "received_data": data,
            "calculated_result": "some calculation"  # 这里可以加入你的计算逻辑
        }
        return result
