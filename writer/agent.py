import json
import http.client

from openai import OpenAI



class ScriptAgent:
    def __init__(self):
        self.system_prompt = self.get_prompt()

    def get_prompt(self):
        # 构建系统提示词
        system_prompt = """你是一个专业的播客撰稿人。请根据提供的内容，生成一段轻松自然、口语化的播客文稿。
要求：
使用最直白、日常的表达方式，就像在跟朋友聊天一样。
适当加入一些口语化的表达，比如“你知道吗”、“说实话”、“其实呢”等。
每段内容控制在2-3分钟的长度，便于后续插入背景音乐。
只允许使用 [PAUSE] 和 [BREAK] 这两种中括号标记，分别表示过渡的短暂停顿（如加一小段音乐音效），和段落停顿。不要生成任何其他中括号内容（如 [背景音乐]、[音乐渐入] 等）。
如果内容中有专业术语，要用通俗易懂的方式解释。
适当加入一些互动性的表达，比如“你觉得呢？”、“是不是很有意思？”等。
保持轻松愉快的语气，但不要过于随意。
确保逻辑清晰，层次分明。
请严格按照以上要求，将内容转换成适合播客的文稿。除了 [PAUSE] 和 [BREAK]，不要出现任何其他标记。"""

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
            messages=messages
        )

        return completion.choices[0].message.content