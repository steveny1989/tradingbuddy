# 自动更新快速开始

## 🚀 三种方案，选一个即可

---

## 方案1: Cron定时任务（最简单）⭐推荐

### 快速配置（3步）

```bash
# 1. 给脚本执行权限
chmod +x scripts/auto_update_cron.sh

# 2. 编辑crontab
crontab -e

# 3. 添加这一行（每天16:30执行，周一到周五）
30 16 * * 1-5 /Users/diyao/tradingbuddy/scripts/auto_update_cron.sh >> /Users/diyao/tradingbuddy/logs/cron.log 2>&1
```

**完成！** 系统会在每个交易日下午4:30自动更新数据。

---

## 方案2: APScheduler调度服务（更灵活）

### 快速配置（2步）

```bash
# 1. 安装依赖
pip install apscheduler

# 2. 后台运行
nohup python3 scripts/scheduler_service.py > logs/scheduler.log 2>&1 &
```

**完成！** 服务会在后台运行，每天16:30自动更新。

---

## 方案3: Systemd服务（Linux服务器，最稳定）

### 快速配置

1. 创建服务文件 `/etc/systemd/system/tradingbuddy-update.service`
2. 创建定时器文件 `/etc/systemd/system/tradingbuddy-update.timer`
3. 启用并启动

详见：`docs/AUTO_UPDATE_GUIDE.md`

---

## ✅ 测试

手动运行测试：

```bash
# 测试自动更新（会检查是否是交易日）
python3 src/app/auto_update.py

# 强制更新（忽略交易日检查）
python3 src/app/auto_update.py --force
```

---

## 📝 说明

- **执行时间**：建议16:30（收盘后30分钟，确保数据已更新）
- **交易日判断**：自动跳过周末和节假日
- **日志位置**：`logs/auto_update_YYYYMMDD.log`

---

## 🔍 查看状态

```bash
# 查看数据库状态
python3 src/app/main.py status

# 查看更新日志
tail -f logs/auto_update_$(date +%Y%m%d).log
```

---

**详细文档**：`docs/AUTO_UPDATE_GUIDE.md`

