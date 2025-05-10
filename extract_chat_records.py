import re
import os
from datetime import datetime

def extract_chat_records(input_file, target_user):
    current_user = None
    records = []
    in_target_section = False
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 检测消息对象分隔线
            if line.startswith('消息对象:'):
                current_user = line.split(':')[1].strip()
                in_target_section = (current_user == target_user)
                continue
                
            # 跳过非目标区域内容
            if not in_target_section:
                continue
                
            # 有效消息记录识别
            if date_pattern.match(line):
                try:
                    # 验证日期格式合法性
                    datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
                    records.append(line)
                except ValueError:
                    pass
            elif records and line:
                # 处理多行消息（如长文本或复制内容）
                records[-1] += '\n' + line

    return records

def save_records(output_file, records):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(records))

if __name__ == '__main__':
    input_file = r'D:\王者荣耀\全部消息记录.txt'     # 完整聊天记录文件路径
    target_user = '人机王者搭子'          # 需要提取的消息对象
    output_dir = './output'  # 或绝对路径如 r'D:\output'
    output_file = os.path.join(output_dir, f'{target_user}.txt')

    # 执行提取并保存
    extracted = extract_chat_records(input_file, target_user)
    save_records(output_file, extracted)
    
    print(f'成功提取 {len(extracted)} 条记录到 {output_file}')