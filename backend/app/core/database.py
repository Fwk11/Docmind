"""
数据库兼容层
============
这个文件只是为了兼容旧的导入路径。

有些代码用 from app.core.database import ...，
有些代码用 from app.db.database import ...，
为了两边都能用，这里把 db/database.py 的内容重新导出一次。

实际代码都在 app/db/database.py 里。
"""

from app.db.database import Base, SessionLocal, engine, get_db_session, init_db  # noqa: F401