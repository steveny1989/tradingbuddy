#!/bin/bash
# 自动数据更新脚本（用于cron）
# 
# 使用方法：
# 1. 给脚本执行权限：chmod +x scripts/auto_update_cron.sh
# 2. 添加到cron：crontab -e
# 3. 添加一行（每天16:30执行）：
#    30 16 * * * /path/to/tradingbuddy/scripts/auto_update_cron.sh >> /path/to/tradingbuddy/logs/cron.log 2>&1

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_DIR"

# 激活Python环境（如果有虚拟环境）
# source venv/bin/activate  # 取消注释以使用虚拟环境

# 运行自动更新
python3 src/app/auto_update.py

# 记录执行时间
echo "$(date): Auto update completed" >> logs/cron.log

