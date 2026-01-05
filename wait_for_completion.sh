#!/bin/bash
# 等待脚本完成并显示最终报告

echo "=========================================="
echo "⏳ 等待更新完成..."
echo "=========================================="
echo ""
echo "脚本正在后台运行，预计还需 40-50 分钟"
echo "你可以："
echo "  1. 运行 './quick_status.sh' 查看进度"
echo "  2. 运行 'tail -f update_log.txt' 查看实时日志"
echo "  3. 按 Ctrl+C 退出等待（不会停止更新）"
echo ""
echo "等待中..."
echo ""

# 等待进程结束
while pgrep -f "update_today.py" > /dev/null; do
    sleep 30
    ./quick_status.sh
    echo ""
done

echo ""
echo "=========================================="
echo "✅ 更新完成！"
echo "=========================================="
echo ""

# 显示最终报告
python3 current_status.py

echo ""
echo "查看完整日志: tail -100 update_log.txt"
echo "=========================================="
