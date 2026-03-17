#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry Manager
重试管理器
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Tuple, Type

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetryError(Exception):
    """重试失败异常"""
    pass

def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger_instance: logging.Logger = None
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay_seconds: 初始延迟 (秒)
        backoff_factor: 退避因子 (每次重试延迟倍数)
        exceptions: 需要重试的异常类型
        logger_instance: 日志记录器
        
    Returns:
        装饰器函数
        
    Example:
        @retry(max_attempts=3, delay_seconds=1, backoff_factor=2)
        def unstable_function():
            pass
    """
    if logger_instance is None:
        logger_instance = logger
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay_seconds
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger_instance.info(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger_instance.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}"
                    )
                    
                    if attempt < max_attempts:
                        logger_instance.info(f"Retrying in {current_delay:.1f} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
            
            logger_instance.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise RetryError(f"Failed after {max_attempts} attempts: {last_exception}")
        
        return wrapper
    return decorator

class RetryManager:
    """重试管理器"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        backoff_factor: float = 2.0
    ):
        """
        初始化重试管理器
        
        Args:
            max_attempts: 最大重试次数
            delay_seconds: 初始延迟 (秒)
            backoff_factor: 退避因子
        """
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds
        self.backoff_factor = backoff_factor
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_retries': 0
        }
    
    def execute(
        self,
        func: Callable,
        *args,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        **kwargs
    ) -> Any:
        """
        执行函数 (带重试)
        
        Args:
            func: 要执行的函数
            args: 位置参数
            exceptions: 需要重试的异常类型
            kwargs: 关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            RetryError: 所有重试都失败
        """
        self.stats['total_calls'] += 1
        current_delay = self.delay_seconds
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                logger.info(f"Execute attempt {attempt}/{self.max_attempts} for {func.__name__}")
                result = func(*args, **kwargs)
                self.stats['successful_calls'] += 1
                return result
            except exceptions as e:
                self.stats['total_retries'] += 1
                logger.warning(
                    f"Execute attempt {attempt}/{self.max_attempts} failed: {e}"
                )
                
                if attempt < self.max_attempts:
                    logger.info(f"Retrying in {current_delay:.1f} seconds...")
                    time.sleep(current_delay)
                    current_delay *= self.backoff_factor
        
        self.stats['failed_calls'] += 1
        logger.error(f"All {self.max_attempts} attempts failed for {func.__name__}")
        raise RetryError(f"Failed after {self.max_attempts} attempts")
    
    def get_stats(self) -> dict:
        """获取重试统计"""
        return self.stats
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_retries': 0
        }

# 示例用法
if __name__ == "__main__":
    # 使用装饰器
    @retry(max_attempts=3, delay_seconds=1, backoff_factor=2)
    def unstable_api_call():
        import random
        if random.random() < 0.7:
            raise ConnectionError("Network error")
        return "Success"
    
    # 测试
    try:
        result = unstable_api_call()
        print(f"Result: {result}")
    except RetryError as e:
        print(f"Failed: {e}")
    
    # 使用管理器
    manager = RetryManager(max_attempts=3, delay_seconds=1)
    
    def another_unstable_function():
        import random
        if random.random() < 0.5:
            raise TimeoutError("Timeout")
        return "Data"
    
    try:
        result = manager.execute(another_unstable_function, exceptions=(TimeoutError,))
        print(f"Result: {result}")
    except RetryError as e:
        print(f"Failed: {e}")
    
    # 查看统计
    print(f"Stats: {manager.get_stats()}")
