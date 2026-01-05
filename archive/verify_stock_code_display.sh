#!/bin/bash

echo "=========================================="
echo "股票代码显示格式验证"
echo "=========================================="
echo ""

echo "检查已修改的文件..."
echo ""

files=(
  "frontend/src/utils/stockCode.ts"
  "frontend/src/pages/SimpleStockDetail.tsx"
  "frontend/src/pages/SimpleStockDetail.premium.tsx"
  "frontend/src/components/picker/DailyPicksCard.tsx"
  "frontend/src/components/picker/WatchlistCard.tsx"
  "frontend/src/components/picker/StrategyPerformanceCard.tsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ $file (文件不存在)"
  fi
done

echo ""
echo "=========================================="
echo "检查 formatStockCode 导入"
echo "=========================================="
echo ""

grep -n "formatStockCode" frontend/src/pages/SimpleStockDetail.tsx
grep -n "formatStockCode" frontend/src/pages/SimpleStockDetail.premium.tsx
grep -n "formatStockCode" frontend/src/components/picker/DailyPicksCard.tsx
grep -n "formatStockCode" frontend/src/components/picker/WatchlistCard.tsx
grep -n "formatStockCode" frontend/src/components/picker/StrategyPerformanceCard.tsx

echo ""
echo "=========================================="
echo "验证完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 重启前端服务: cd frontend && npm start"
echo "2. 访问 http://localhost:3000/picker"
echo "3. 检查股票代码显示是否为纯数字格式"
echo ""
