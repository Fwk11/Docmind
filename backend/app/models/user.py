"""
用户数据模型
============
对应数据库中的 users 表，存储用户账号和密码。

密码安全说明：
- 密码绝对不能明文存储！如果数据库泄露，用户的密码就暴露了
- 我们使用 PBKDF2-HMAC-SHA256 算法对密码进行哈希
- 哈希 = 把密码变成一串不可逆的乱码，无法从乱码反推出原始密码
- 存储格式：salt:hash（盐值:哈希值）

为什么用 PBKDF2 而不是 bcrypt？
- bcrypt 限制密码长度为 72 字节，超过的部分会被截断
- PBKDF2 没有这个限制，更安全
- 100000 次迭代让暴力破解变得非常慢

类比：密码哈希就像把信放进碎纸机，碎出来的纸屑无法拼回原信，
但你可以用同一封信再碎一次，对比纸屑是否一样来验证密码。
"""

import hashlib
import os
import hmac

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    """用户模型：映射到 users 表"""
    __tablename__ = "users"

    # 主键：自增 ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 用户名：最长 64 字符，唯一（不能重复），加索引加速查询
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    # 哈希后的密码：格式为 "salt:hash"，最长 256 字符
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希处理

        步骤：
        1. 生成随机盐值（salt）：16 字节的随机数，每次不同
        2. 用 PBKDF2 算法迭代 100000 次计算哈希值
        3. 返回 "盐值:哈希值" 格式的字符串

        盐值有什么用？
        - 防止彩虹表攻击（预先计算好的密码-哈希对照表）
        - 即使两个用户密码相同，因为盐值不同，哈希值也不同
        """
        salt = os.urandom(16).hex()
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
        return f"{salt}:{hashed}"

    def verify_password(self, password: str) -> bool:
        """
        验证密码是否正确

        步骤：
        1. 从存储的哈希值中取出盐值
        2. 用相同的盐值和算法对输入密码计算哈希
        3. 用 hmac.compare_digest 安全比较两个哈希值

        为什么用 hmac.compare_digest 而不是 ==？
        - == 比较遇到第一个不同的字符就返回，可能被计时攻击
        - compare_digest 无论是否匹配都花相同时间，更安全
        """
        try:
            salt, stored_hash = self.hashed_password.split(":", 1)
            computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
            return hmac.compare_digest(computed, stored_hash)
        except (ValueError, AttributeError):
            # 哈希值格式不正确，验证失败
            return False