import os
import base64
from typing import List, Tuple, Union
import re



def process_markdown_file(file_path: str) -> List[Tuple[str, Union[str, bytes]]]:
    """
    处理markdown文件，将内容分割成文本块和图片块，并去除<div>标签，仅保留内部文本
    
    Args:
        file_path: markdown文件的路径
        
    Returns:
        List[Tuple[str, Union[str, bytes]]]: 包含(类型, 内容)的元组列表
        类型可以是 'text' 或 'image'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 先处理<div>标签，去掉样式和标签，只保留内部文本
    def div_replacer(match):
        inner = match.group(1)
        return inner.strip()
    # 匹配 <div ...>...</div>，支持多行和带属性
    content = re.sub(r'<div[^>]*>(.*?)</div>', div_replacer, content, flags=re.DOTALL)
    
    # 使用正则表达式匹配HTML格式的图片标签
    image_pattern = r'<figure>\s*<img\s+src="([^"]+)"[^>]*>.*?</figure>'
    
    blocks = []
    last_end = 0
    
    for match in re.finditer(image_pattern, content, re.DOTALL):
        # 添加图片前的文本块
        if match.start() > last_end:
            text_block = content[last_end:match.start()].strip()
            if text_block:
                blocks.append(('text', text_block))
        # 处理图片
        image_path = match.group(1)
        if os.path.isabs(image_path):
            try:
                with open(image_path, 'rb') as img_file:
                    image_data = base64.b64encode(img_file.read())
                    blocks.append(('image', image_data))
            except Exception as e:
                print(f"无法读取图片 {image_path}: {str(e)}")
        last_end = match.end()
    # 添加最后一个文本块
    if last_end < len(content):
        text_block = content[last_end:].strip()
        if text_block:
            blocks.append(('text', text_block))
    return blocks

# 使用示例
if __name__ == "__main__":
    try:
        blocks = process_markdown_file("./assets/docs/营销学.md")
        print(len(blocks))
        for block_type, content in blocks:
            if block_type == 'text':
                print(content)
            else:
                print(f"图片块: {content[:50]}...")
    except Exception as e:
        print(f"处理文件时出错: {str(e)}") 