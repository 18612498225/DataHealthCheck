# -*- coding: utf-8 -*-
"""
文件名: data_loader.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 从 CSV 加载数据
"""
import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def load_csv_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load data from a CSV file.

    Args:
        file_path: The path to the CSV file.

    Returns:
        A pandas DataFrame containing the data from the CSV file, 
        or None if an error occurs.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        logger.error("文件不存在: %s", file_path)
        return None
    except pd.errors.EmptyDataError:
        logger.warning("文件为空: %s", file_path)
        return None
    except pd.errors.ParserError:
        logger.error("CSV 解析失败: %s", file_path)
        return None
    except Exception as e:
        logger.exception("加载数据时发生异常: %s", e)
        return None
