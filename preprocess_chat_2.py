import re
import os
import json
from datetime import datetime

def parse_chat(file_path, output_file, max_lines=-1): # max_lines设置最长读取文件行数，-1代表一直读到文件末尾
    # ====== 1. 通用消息解析 ======
    with open(file_path, "r", encoding="utf-8") as f:
        if max_lines != -1:
            # 智能读取前N行（保留最后一条完整消息）
            buffer = []
            line_count = 0
            while line_count < max_lines:
                line = f.readline()
                if not line:
                    break
                buffer.append(line)
                # 遇到新消息头时重置计数器
                if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ", line):
                    line_count += 1

            text = "".join(buffer).replace('\u200b', '')
        else:
            text = f.read().replace('\u200b', '')
    
    # 增强型正则表达式（兼容名称变化）
    pattern = r"""
    (
        (?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})
        \s+
        (?P<sender>(?!柚子茶)[^\r\n]+)
        (?:\r\n|\n)+
        (?P<content>.*?)
        (?=\n\d{4}-\d{2}-\d{2}\s|\Z)
    |
        (?P<yuzu_timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})
        \s+柚子茶
        (?:\r\n|\n)+
        (?P<yuzu_content>.*?)
        (?=\n\d{4}-|\Z)
    )
    """
    
    messages = []
    for match in re.finditer(pattern, text, re.VERBOSE|re.DOTALL):
        # 处理用户发言
        if match.group("yuzu_timestamp"):
            messages.append({
                "timestamp": datetime.strptime(match.group("yuzu_timestamp"), "%Y-%m-%d %H:%M:%S"),
                "sender": "柚子茶",
                "content": match.group("yuzu_content").strip().replace('\n', ' ')
            })
        # 处理朋友发言（任何非用户）
        elif match.group("timestamp"):
            try:
                messages.append({
                    "timestamp": datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S"),
                    "sender": "朋友",  # 统一标记为"朋友"
                    "content": match.group("content").strip().replace('\n', ' ')
                })
            except ValueError:
                continue

    # ====== 2. 智能对话配对 ======
    conversation_pairs = []
    conversation_pairs_json = []
    last_user_msg = None
    
    for msg in messages:
        if msg["sender"] == "柚子茶":
            # 累积上下文（支持用户连续发言）
            if last_user_msg:
                last_user_msg["content"] += " [继续] " + msg["content"]
            else:
                last_user_msg = msg.copy()
        elif last_user_msg:
            # 捕获第一个朋友回复
            conversation_pairs.append({
                "context": last_user_msg["content"],
                "response": msg["content"],
                "timestamp": msg["timestamp"]
            })
            conversation_pairs_json.append({
                "context": last_user_msg["content"],
                "response": msg["content"]
            })
            last_user_msg = None  # 重置
    
    print(f"生成对话对：{len(conversation_pairs)}组（示例：）")
    # # 打印每对对话内容
    # if conversation_pairs:
    #     for i in range(len(conversation_pairs)):
    #         print(f"示例上下文：{conversation_pairs[i]['context'][:30]}")
    #         print(f"示例回复：{conversation_pairs[i]['response'][:30]}")
    # 将对话对写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversation_pairs_json, f, ensure_ascii=False, indent=4)
    
    return conversation_pairs

# 使用示例
input_dir = './output'  # 或绝对路径如 r'D:\output'
output_dir = './output'  # 或绝对路径如 r'D:\output'
target_user = '人机王者搭子'          # 需要提取的消息对象
input_file = os.path.join(input_dir, f'{target_user}_1.txt')
output_file = os.path.join(output_dir, f'{target_user}_conversation_pairs.json')

pairs = parse_chat(input_file, output_file)

# 得到以下形式的对话对
# 示例上下文：不能 太糊了 [继续] 要打字
# 示例回复：2005
# 示例上下文：发过去了 [继续] 眼睛痛，还要休息一下 [继续] 你先玩吧
# 示例回复：忘了同意了

# 下一步就是把上下文和回复组织起来，变成向量存在向量库中。