#!/bin/bash

echo "================================================"
echo "🚀 A股全市场数据下载"
echo "================================================"
echo ""
echo "即将下载 5792 只股票的历史数据"
echo "预计时间: 40分钟 - 2小时"
echo "数据大小: 约 300MB"
echo ""
echo "特点:"
echo "  ✓ 可随时中断（Ctrl+C）"
echo "  ✓ 支持断点续传"
echo "  ✓ 自动重试失败"
echo ""
read -p "确认开始下载？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "开始下载..."
    echo "================================================"
    python3 main.py download
    
    echo ""
    echo "================================================"
    echo "✨ 下载完成！"
    echo "================================================"
    echo ""
    echo "查看状态: python3 main.py status"
    echo "检查数据: python3 tools/inspect_database.py"
    echo ""
else
    echo "已取消"
fi
