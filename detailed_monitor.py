#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""详细监控更新进度"""
import re
import time
from datetime import datetime

def monitor_log():
    """监控日志文件"""
    print("="*60)
    print("📊 实时监控更新日志")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    last_position = 0
    
    try:
        while True:
            with open('update_log.txt', 'r', encoding='utf-8') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                last_position = f.tell()
                
                for line in new_lines:
                    # 提取进度信息
                    if '更新进度:' in line and 'it/s' in line:
                        # 提取关键信息
                        match = re.search(r'(\d+)/(\d+).*?(\d+\.\d+)it/s.*?成功=(\d+).*?失败=(\d+).*?记录=(\d+)', line)
                        if match:
                            current, total, speed, success, failed, records = match.groups()
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            progress = int(current) / int(total) * 100
                            print(f"[{timestamp}] 进度: {current}/{total} ({progress:.1f}%) | "
                                  f"成功: {success} | 失败: {failed} | 记录: {records} | "
                                  f"速度: {speed} it/s")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("✅ 监控已停止")
        print("="*60)
    except FileNotFoundError:
        print("❌ 找不到 update_log.txt 文件")

if __name__ == "__main__":
    monitor_log()
