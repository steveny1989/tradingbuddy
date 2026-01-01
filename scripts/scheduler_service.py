#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度服务
使用APScheduler在交易日收盘后自动更新数据

安装依赖：
pip install apscheduler

使用方法：
1. 直接运行：python3 scripts/scheduler_service.py
2. 后台运行：nohup python3 scripts/scheduler_service.py > logs/scheduler.log 2>&1 &
3. 使用systemd（推荐）：见 scripts/tradingbuddy.service
"""
import sys
import logging
from pathlib import Path
from datetime import datetime, time

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.app.auto_update import run_auto_update

# 配置日志
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def job_function():
    """定时任务函数"""
    logger.info("="*60)
    logger.info("定时任务触发：开始自动更新数据")
    logger.info("="*60)
    
    try:
        result = run_auto_update()
        if result['success']:
            logger.info("✅ 定时更新成功")
        else:
            logger.warning(f"⚠️  定时更新跳过: {result.get('message', '未知原因')}")
    except Exception as e:
        logger.error(f"❌ 定时更新失败: {e}", exc_info=True)


def main():
    """主函数"""
    scheduler = BlockingScheduler()
    
    # 配置定时任务：每个工作日（周一到周五）16:30执行
    # 注意：这里只检查工作日，是否交易日由run_auto_update内部判断
    scheduler.add_job(
        func=job_function,
        trigger=CronTrigger(
            day_of_week='mon-fri',  # 周一到周五
            hour=16,                # 16点
            minute=30,              # 30分
            timezone='Asia/Shanghai'  # 时区
        ),
        id='daily_update',
        name='每日数据更新',
        replace_existing=True
    )
    
    logger.info("="*60)
    logger.info("📅 定时任务调度服务启动")
    logger.info("="*60)
    logger.info("计划任务：")
    logger.info("  - 每个工作日 16:30 自动更新数据")
    logger.info("  - 时区：Asia/Shanghai")
    logger.info("="*60)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("定时任务调度服务停止")
        scheduler.shutdown()


if __name__ == "__main__":
    main()

