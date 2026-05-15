"""SQLite 数据库连接层，封装查询和写入操作"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Any


class DatabaseError(Exception):
    """数据库操作异常基类"""
    pass


_DB_PATH: str | None = None


def set_db_path(path: str) -> None:
    """设置数据库文件路径（App 启动时调用）"""
    global _DB_PATH
    _DB_PATH = path


def get_db_path() -> str:
    """获取数据库路径，首次调用时初始化为默认路径（父目录的 inventory.db）"""
    global _DB_PATH
    if _DB_PATH is None:
        # 默认路径：与 Flask 端 app.py 共用父目录的 inventory.db
        _DB_PATH = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'inventory.db'
        )
    return _DB_PATH


def _connect(read_only: bool = True) -> sqlite3.Connection:
    """创建数据库连接（内部使用）"""
    path = get_db_path()
    if read_only:
        uri = f'file:{path}?mode=ro'
        conn = sqlite3.connect(uri, uri=True)
    else:
        conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    """执行查询，返回字典列表"""
    conn = _connect(read_only=True)
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise DatabaseError(f"查询失败: {e}") from e
    finally:
        conn.close()


def get(sql: str, params: tuple = ()) -> dict[str, Any] | None:
    """执行查询，返回单条字典或 None"""
    conn = _connect(read_only=True)
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        raise DatabaseError(f"查询失败: {e}") from e
    finally:
        conn.close()


def execute(sql: str, params: tuple = ()) -> int:
    """执行单条写入操作（INSERT/UPDATE/DELETE），返回受影响行数"""
    conn = _connect(read_only=False)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        raise DatabaseError(f"写入失败: {e}") from e
    finally:
        conn.close()


@contextmanager
def transaction():
    """事务上下文管理器，支持多条写入操作原子提交"""
    conn = _connect(read_only=False)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"事务失败: {e}") from e
    finally:
        conn.close()
