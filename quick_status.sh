#!/bin/bash
# 快速查看更新状态

echo "=========================================="
echo "📊 快速状态检查"
echo "=========================================="
echo ""

# 检查进程是否在运行
if pgrep -f "update_today.py" > /dev/null; then
    echo "✅ 脚本正在运行"
else
    echo "⏸️  脚本已停止"
fi

echo ""

# 显示最新进度
echo "📈 最新进度:"
tail -1 update_log.txt | grep -o '[0-9]*/[0-9]*' | head -1 | awk -F'/' '{printf "   %s/%s 只股票 (%.1f%%)\n", $1, $2, ($1/$2)*100}'

echo ""

# 显示数据库状态
echo "💾 数据库状态:"
sqlite3 data/raw/daily_raw.db "SELECT '   2026-01-05: ' || COUNT(*) || ' 条记录' FROM daily_raw WHERE date = '2026-01-05'"

echo ""
echo "=========================================="
echo "💡 提示: 运行 'python3 current_status.py' 查看详细状态"
echo "=========================================="
