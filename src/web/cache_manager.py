"""
选股结果缓存管理器
使用内存缓存 + 后台刷新机制
"""
import threading
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class PickerCache:
    """选股结果缓存"""
    
    def __init__(self):
        self._daily_picks: List[Dict] = []
        self._last_update: Optional[datetime] = None
        self._is_updating: bool = False
        self._lock = threading.Lock()
        
    def get_daily_picks(self) -> List[Dict]:
        """获取今日精选（从缓存）"""
        with self._lock:
            return self._daily_picks.copy()
    
    def set_daily_picks(self, picks: List[Dict]):
        """更新今日精选缓存"""
        with self._lock:
            self._daily_picks = picks
            self._last_update = datetime.now()
            logger.info(f"缓存已更新: {len(picks)} 只股票")
    
    def get_last_update(self) -> Optional[datetime]:
        """获取最后更新时间"""
        with self._lock:
            return self._last_update
    
    def is_updating(self) -> bool:
        """是否正在更新"""
        with self._lock:
            return self._is_updating
    
    def set_updating(self, status: bool):
        """设置更新状态"""
        with self._lock:
            self._is_updating = status


# 全局缓存实例
_cache = PickerCache()


def get_cache() -> PickerCache:
    """获取缓存实例"""
    return _cache


def refresh_cache_async(scan_function):
    """异步刷新缓存"""
    def _refresh():
        cache = get_cache()
        if cache.is_updating():
            logger.info("缓存正在更新中，跳过本次刷新")
            return
        
        try:
            cache.set_updating(True)
            logger.info("开始刷新缓存...")
            
            # 执行扫描
            picks = scan_function()
            
            # 更新缓存
            cache.set_daily_picks(picks)
            
            logger.info(f"缓存刷新完成: {len(picks)} 只股票")
        except Exception as e:
            logger.error(f"缓存刷新失败: {e}", exc_info=True)
        finally:
            cache.set_updating(False)
    
    # 在后台线程中执行
    thread = threading.Thread(target=_refresh, daemon=True)
    thread.start()


def init_cache(scan_function):
    """初始化缓存（启动时调用）"""
    logger.info("初始化缓存...")
    refresh_cache_async(scan_function)
