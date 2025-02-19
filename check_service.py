class CheckService:
    def process_data(self, data):
        # 这里放你的业务逻辑
        result = {
            "message": "Processed by CheckService",
            "received_data": data,
            "calculated_result": "some calculation"  # 这里可以加入你的计算逻辑
        }
        return result
