import re
import os
from datetime import datetime

def preprocess_chat(input_path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 优化正则表达式（增加全角符号支持）
    msg_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} .+)')
    tag_pattern = re.compile(r'\[(?:表情|图片)\]')  # 使用非捕获组
    
    # 新增分隔线检测模式
    separator_pattern = re.compile(r'^=+.*|=+$')  # 匹配任意数量等号开头/结尾

    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        current_msg = []
        valid_count = 0
        
        for raw_line in infile:
            line = raw_line.rstrip('\n')
            
            # 过滤分隔线和消息分组信息（新增逻辑）
            if separator_pattern.match(line) or '消息分组:' in line:
                continue
                
            # 消息头检测
            if msg_pattern.match(line):
                # 处理已收集消息
                if current_msg:
                    header, *content = current_msg
                    cleaned_content = process_content(content, tag_pattern)
                    if cleaned_content:
                        outfile.write(f"{header}\n{cleaned_content}\n\n")
                        valid_count += 1
                # 开始新消息
                current_msg = [line]
            else:
                current_msg.append(line)
        
        # 处理最后一条消息
        if current_msg:
            header, *content = current_msg
            cleaned_content = process_content(content, tag_pattern)
            if cleaned_content:
                outfile.write(f"{header}\n{cleaned_content}\n")
                valid_count += 1

        print(f"处理完成！有效消息数：{valid_count}")

def process_content(content_lines, pattern):
    # 逐行处理优化（解决多行消息问题）
    cleaned_lines = []
    has_valid_content = False
    
    for line in content_lines:
        # 替换标签并去除两端空格
        cleaned_line = pattern.sub('', line).strip()
        
        # 保留非空行原始缩进（仅去除标签）
        original_line = pattern.sub('', line).rstrip()
        
        if cleaned_line:  # 存在有效内容
            has_valid_content = True
            cleaned_lines.append(original_line)
        elif original_line:  # 保留空白行但无标签的情况
            cleaned_lines.append(original_line)
    
    # 根据规则过滤消息
    if not has_valid_content:
        return ''
    
    return '\n'.join(cleaned_lines)


if __name__ == '__main__':
    input_dir = './output'  # 或绝对路径如 r'D:\output'
    output_dir = './output'  # 或绝对路径如 r'D:\output'
    target_user = '人机王者搭子'          # 需要提取的消息对象
    input_file = os.path.join(input_dir, f'{target_user}.txt')
    output_file = os.path.join(output_dir, f'{target_user}_1.txt')
    
    preprocess_chat(input_file, output_file)