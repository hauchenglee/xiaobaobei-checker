class AIProcess:
    def __init__(self):
        pass

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

    def process_data(self, article, corrected_text):
        all_errors = self.find_differences(article, corrected_text)
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
