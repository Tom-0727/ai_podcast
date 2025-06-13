import json
import http.client

from openai import OpenAI



class ScriptAgent:
    def __init__(self):
        self.system_prompt = self.get_prompt()

    def get_prompt(self):
        # 构建系统提示词
        system_prompt = """你是一个专业的播客撰稿人。请根据提供的内容，生成播客文稿。
要求：
1. 使用直白、日常的表达方式，但不乏专业度。适当加入一些口语化的表达，比如"说实话"、"其实呢"等。
2. 可以使用两种标记控制节奏，[-]表示短暂停顿，[!]表示强调。
3. 适当加入一些互动性的表达。
4. 尽量忠实于原文，用原文的表述，对于原文太过简略的内容适当补充。
请严格按照以上要求，将内容转换成适合播客的文稿。"""

        return system_prompt
    
    def script_make(self, md_content):
        # 构建用户消息
        user_content = []
        for block_type, content in md_content:
            if block_type == 'text':
                user_content.append({
                    "type": "text",
                    "text": content
                })
            elif block_type == 'image':
                user_content.append({
                    "type": "image",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{content.decode('utf-8')}"
                    }
                })

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        return messages

    def one_shot(self, messages):
        raise NotImplementedError("Subclass must implement this method")


class OpenAIScriptAgent(ScriptAgent):
    def __init__(self, openai_key, model="gpt-4o-2024-08-06"):
        self.client = OpenAI(api_key=openai_key)
        self.model = model
        super().__init__()

    def one_shot(self, messages):
        # 处理消息中的图片格式
        for msg in messages:
            if isinstance(msg["content"], list):
                for item in msg["content"]:
                    if item["type"] == "image":
                        # OpenAI格式：使用input_image
                        item["type"] = "input_image"

        completion = self.client.chat.completions.create(
            model=self.model,
            store=True,
            temperature=0.175,
            messages=messages
        )
        return completion.choices[0].message.content


class API2DScriptAgent(ScriptAgent):
    def __init__(self, forward_key, model="gpt-4o-2024-08-06"):
        self.conn = http.client.HTTPSConnection("oa.api2d.net")
        self.model = model
        self.headers = {
            'Authorization': f'Bearer {forward_key}',
            'Content-Type': 'application/json'
        }
        super().__init__()

    def one_shot(self, messages, image_mode='image'):
        # 处理消息中的图片格式
        for msg in messages:
            if isinstance(msg["content"], list):
                for item in msg["content"]:
                    if item["type"] == "image":
                        # API2D格式：使用image
                        item["type"] = image_mode

        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "safe_mode": False
        })
        self.conn.request("POST", "/v1/chat/completions", payload, self.headers)
        res = self.conn.getresponse()
        data = res.read()
        resp = data.decode("utf-8")
        resp = eval(resp.replace('null', '0'))

        return resp['choices'][0]['message']['content']
    

class QwenScriptAgent(ScriptAgent):
    def __init__(self, key, model="qwen-plus-latest"):
        self.client = OpenAI(
            api_key=key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = model
        super().__init__()

    def one_shot(self, messages):
        # 处理消息中的图片格式
        for msg in messages:
            if isinstance(msg["content"], list):
                for item in msg["content"]:
                    if item["type"] == "image":
                        # Qwen格式：使用image_url
                        item["type"] = "image_url"

        completion = self.client.chat.completions.create(
            model=self.model,
            stream=True,  # 启用流式输出
            messages=messages
        )
        
        # 处理流式响应
        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
        return full_response