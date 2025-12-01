import json
import requests
import os
import shutil

class Filter:
    def __init__(self, config):
        self.config = config

    def keywords_filter(self, text, keywords_rule):
        if not keywords_rule.strip():
            return False
        or_groups = [group.strip() for group in keywords_rule.split(',')]
        for group in or_groups:
            # Split by + for AND keywords
            and_keywords = [kw.strip() for kw in group.split('+')]
            # Check if all AND keywords are in the text (case-insensitive)
            if all(kw.lower() in text.lower() for kw in and_keywords):
                return True
        return False

    # -------- AI 相关功能 (OpenAI Compatible) --------
    def openai_run(self, model, inputs):
        # 获取配置，支持自定义 Base URL (例如用于 OneAPI 或其他中转)
        api_key = self.config.get('openai_api_key', '')
        base_url = self.config.get('openai_base_url', 'https://api.openai.com/v1')
        
        # 构造请求 URL，确保指向 chat/completions
        if not base_url.endswith('/'):
            base_url += '/'
        url = f"{base_url}chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": inputs,
            "temperature": 0.7 
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code != 200:
                print(f"AI API Error: {response.text}")
                return None
            return response.json()
        except Exception as e:
            print(f"Request Exception: {e}")
            return None

    def ai_filter(self, description, prompt):
        print('Using AI Model:', self.config.get('model'))
        inputs = [
            { "role": "system", "content": prompt},
            { "role": "user", "content": description}
        ]
        
        output = self.openai_run(self.config['model'], inputs)
        
        if output and 'choices' in output and len(output['choices']) > 0:
            content = output['choices'][0]['message']['content']
            # 保留原本的逻辑，分割 END
            return content.split('END')[0]
        else:
            print("AI response parsing failed or empty")
            return "AI Processing Failed"
