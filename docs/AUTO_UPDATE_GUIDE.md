# 自动数据更新指南

本文档介绍如何配置自动数据更新，让系统在每个交易日后自动收集数据，无需人工操作。

---

## 🎯 方案概览

### 方案1: Cron定时任务（推荐，简单）⭐
- **优点**：简单直接，系统原生支持
- **缺点**：只能按固定时间执行，无法精确判断交易日
- **适用**：Linux/Mac系统

### 方案2: APScheduler调度服务（推荐，灵活）⭐⭐
- **优点**：灵活，可以在Python中判断交易日
- **缺点**：需要常驻进程
- **适用**：所有平台，需要精确控制

### 方案3: Systemd服务（推荐，稳定）⭐⭐⭐
- **优点**：系统级服务，自动重启，日志管理完善
- **缺点**：仅限Linux系统
- **适用**：Linux服务器

---

## 📋 方案1: Cron定时任务

### 步骤1: 创建执行脚本

脚本已创建在 `scripts/auto_update_cron.sh`

```bash
# 给脚本执行权限
chmod +x scripts/auto_update_cron.sh
```

### 步骤2: 测试脚本

```bash
# 手动运行测试
./scripts/auto_update_cron.sh
```

### 步骤3: 配置Cron

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天16:30执行）
30 16 * * 1-5 /path/to/tradingbuddy/scripts/auto_update_cron.sh >> /path/to/tradingbuddy/logs/cron.log 2>&1

# 说明：
# 30 16     - 16:30执行
# * * 1-5   - 周一到周五
# 最后的 >> ... 是日志重定向
```

### 步骤4: 验证Cron配置

```bash
# 查看crontab列表
crontab -l

# 查看日志
tail -f logs/cron.log
```

---

## 📋 方案2: APScheduler调度服务

### 步骤1: 安装依赖

```bash
pip install apscheduler
```

### 步骤2: 运行调度服务

```bash
# 直接运行（前台）
python3 scripts/scheduler_service.py

# 后台运行
nohup python3 scripts/scheduler_service.py > logs/scheduler.log 2>&1 &

# 查看进程
ps aux | grep scheduler_service

# 查看日志
tail -f logs/scheduler.log
```

### 步骤3: 停止服务

```bash
# 查找进程ID
ps aux | grep scheduler_service

# 停止进程
kill <PID>
```

---

## 📋 方案3: Systemd服务（Linux）

### 步骤1: 创建服务文件

创建文件 `/etc/systemd/system/tradingbuddy-update.service`：

```ini
[Unit]
Description=TradingBuddy Auto Update Service
After=network.target

[Service]
Type=simple
User=your_username  # 改为你的用户名
WorkingDirectory=/path/to/tradingbuddy
ExecStart=/usr/bin/python3 /path/to/tradingbuddy/src/app/auto_update.py
Restart=on-failure
RestartSec=60

# 日志
StandardOutput=append:/path/to/tradingbuddy/logs/systemd.log
StandardError=append:/path/to/tradingbuddy/logs/systemd_error.log

[Install]
WantedBy=multi-user.target
```

### 步骤2: 创建定时器文件

创建文件 `/etc/systemd/system/tradingbuddy-update.timer`：

```ini
[Unit]
Description=Run TradingBuddy Update Daily
Requires=tradingbuddy-update.service

[Timer]
# 每个工作日16:30执行
OnCalendar=Mon..Fri 16:30:00
TimeZone=Asia/Shanghai

[Install]
WantedBy=timers.target
```

### 步骤3: 启用和启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用定时器
sudo systemctl enable tradingbuddy-update.timer

# 启动定时器
sudo systemctl start tradingbuddy-update.timer

# 查看状态
sudo systemctl status tradingbuddy-update.timer

# 查看服务日志
sudo journalctl -u tradingbuddy-update.service -f
```

---

## 🔍 交易日判断

系统会自动判断是否是交易日：

1. **周末检测**：自动跳过周六、周日
2. **节假日检测**：通过查询上证指数数据判断
3. **手动跳过**：如果不是交易日，自动跳过更新

### 手动运行（忽略交易日检查）

```bash
# 强制更新（不检查是否是交易日）
python3 src/app/auto_update.py --force

# 指定日期更新
python3 src/app/auto_update.py --date 20250102
```

---

## 📊 执行时间建议

### 推荐时间：**16:30**（收盘后30分钟）

- ✅ 市场已收盘（15:00收盘）
- ✅ 数据已更新（通常需要10-30分钟）
- ✅ 避开交易时间

### 备选时间

- **16:00**：收盘后立即（可能数据未完全更新）
- **17:00**：更安全，但可能延迟
- **20:00**：晚上执行（确保数据完整）

---

## 🔔 通知和监控

### 邮件通知（可选）

修改 `src/app/auto_update.py`，在更新完成后发送邮件：

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(result):
    """发送通知邮件"""
    # 实现邮件发送逻辑
    pass
```

### 日志监控

```bash
# 实时查看日志
tail -f logs/auto_update_$(date +%Y%m%d).log

# 查看最近的更新记录
grep "自动更新完成" logs/auto_update_*.log | tail -10

# 查看错误
grep "ERROR" logs/auto_update_*.log
```

---

## ⚠️ 注意事项

### 1. 数据源限制
- AKShare API可能有频率限制
- 建议添加重试机制和限速

### 2. 网络问题
- 确保网络连接稳定
- 可以添加网络检测

### 3. 数据完整性
- 如果更新失败，会记录日志
- 可以手动重新运行

### 4. 节假日处理
- 系统会自动跳过非交易日
- 长假后可能需要手动检查

---

## 🧪 测试

### 测试自动更新脚本

```bash
# 测试今天的更新
python3 src/app/auto_update.py

# 测试指定日期
python3 src/app/auto_update.py --date 20250102

# 强制更新（忽略交易日检查）
python3 src/app/auto_update.py --force
```

### 测试Cron配置

```bash
# 修改cron为每分钟执行一次（测试用）
* * * * * /path/to/tradingbuddy/scripts/auto_update_cron.sh

# 查看日志
tail -f logs/cron.log
```

---

## 📝 常见问题

### Q: Cron任务没有执行？

A: 检查：
1. Cron服务是否运行：`systemctl status cron`（Ubuntu）或 `systemctl status crond`（CentOS）
2. 脚本是否有执行权限：`chmod +x scripts/auto_update_cron.sh`
3. 路径是否正确（使用绝对路径）
4. 查看日志：`tail -f logs/cron.log`

### Q: 如何修改执行时间？

A: 
- **Cron**: 修改crontab中的时间配置
- **APScheduler**: 修改 `scripts/scheduler_service.py` 中的CronTrigger
- **Systemd**: 修改timer文件中的OnCalendar

### Q: 如何查看更新状态？

A:
```bash
# 查看数据库状态
python3 src/app/main.py status

# 查看最近更新的日志
ls -lt logs/auto_update_*.log | head -5
```

---

## 🎯 推荐配置

对于大多数用户，推荐使用**方案1（Cron）**或**方案3（Systemd）**：

- **个人电脑/开发环境**：方案1（Cron）
- **Linux服务器**：方案3（Systemd）

配置完成后，系统会在每个交易日的收盘后自动更新数据，完全无需人工干预！

---

**更新时间**: 2026-01-01

