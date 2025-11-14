import binascii
from .logger import logger
from typing import Optional, Any, Dict, List


class KeyBuilder:
    """
    Redis ORM 的 Key 构造器。
    用于生成统一的 Redis key，支持 shard_tag、namespace、动态参数等。

    示例：
        builder = KeyBuilder(namespace="user_service", shard_tag="user:42")
        builder.build(model="UserModel", key_id="42")
        # => "user_service:UserModel:{user:42}:42"
    """

    def __init__(
            self,
            namespace: str = "default",
            delimiter: str = ":",
            shard_tag: Optional[List[str]] = None,
            hash_slot_tag_enable: bool = True,
            static_prefix: Optional[str] = None,
    ):
        """
        初始化 KeyBuilder。

        :param namespace: 命名空间，通常为服务或应用名。
        :param delimiter: 分隔符，默认 ":"。
        :param shard_tag: 用于 Redis Cluster 的分片标签，例如 "user:123"。
        :param hash_slot_tag_enable: 是否在 key 中启用 {tag} 包裹以确保 Cluster 一致路由。
        :param static_prefix: 静态前缀（如 env:prod/test）。
        """
        self.namespace = namespace
        self.delimiter = delimiter
        self.shard_tag = shard_tag or []
        self.hash_slot_tag_enable = hash_slot_tag_enable
        self.static_prefix = static_prefix
        if not self.hash_slot_tag_enable:
            logger.warning(
                'Please ensure that you are not using the Redis Cluster mode; '
                'otherwise, '
                'the primary key consistency between the standalone mode and the Cluster mode '
                'will not be compatible'
            )

    def build(self, model: str, key_id: Optional[Any] = None, extra: Optional[Dict[str, Any]] = None) -> str:
        """
        构建 Redis key。

        :param model: 模型名称，例如 "UserModel"。
        :param key_id: 主键 ID 或唯一标识。
        :param extra: 附加字段（dict），例如 {"field": "name"}。
        :return: 完整 Redis key 字符串。
        """
        parts = []

        # 环境前缀
        if self.static_prefix:
            parts.append(self.static_prefix)

        # 命名空间
        parts.append(self.namespace)

        # 模型名
        parts.append(model)

        # shard tag
        if self.shard_tag:
            tag = f"{{{self.shard_tag}}}" if self.hash_slot_tag_enable else self.shard_tag
            parts.append(tag)

        # key_id
        if key_id is not None:
            parts.append(str(key_id))

        # 附加参数
        if extra:
            for k, v in extra.items():
                parts.append(f"{k}={v}")

        return self.delimiter.join(parts)

    @staticmethod
    def extract_hash_tag(key: str) -> Optional[str]:
        """提取 Redis Cluster 中的 {tag} 内容"""
        if "{" in key and "}" in key:
            start = key.index("{") + 1
            end = key.index("}")
            return key[start:end]
        return None

    @staticmethod
    def compute_slot(tag: str) -> int:
        """根据 tag 模拟计算 Redis cluster slot (CRC16 % 16384)"""
        slot = binascii.crc_hqx(tag.encode("utf-8"), 0) % 16384
        return slot

    def build_with_template(self, template: str, **kwargs) -> str:
        """
        使用模板构建 key，例如：
            builder.build_with_template("user:{uid}:profile", uid=42)
            => "user:{uid}:profile" -> "user:42:profile"
        """
        key = template.format(**kwargs)
        if self.hash_slot_tag_enable and self.shard_tag and "{" not in key:
            # 自动补充 shard_tag 以兼容 cluster
            key = f"{key}{{{self.shard_tag}}}"
        return key
