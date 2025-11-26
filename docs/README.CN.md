# FlameModel 中文指南

FlameModel 是一个基于 Pydantic 的 Redis 数据建模与操作框架。它为 Redis 的多种原生数据结构（string、hash、list、set、zset、geo、bitmap、hyperloglog、stream）提供统一的模型定义与类型安全的操作接口，内置键生成策略、可配置序列化器、同步/异步运行模式，以及事务与序列化执行流程。

---

## 设计目标

- 提供面向对象、类型安全的 Redis 数据建模体验。
- 覆盖 Redis 常用数据结构，统一 `save/get/delete/expire` 等操作风格。
- 支持同步与异步两种运行模式，同一套 API 兼容两种模式。
- 可插拔的键生成器（KeyBuilder）与序列化器（Serializer）。
- 自动注册模型，简化使用者的接入成本。

---

## 架构总览

- 核心模块（`core/`）
  - 键生成器：`DefaultKeyBuilder`，统一构造主键、索引、唯一约束、关系等键格式。
  - 序列化器：`DefaultSerializer`，基于 Pydantic 2 序列化/反序列化。
- 适配器（`adaptor/`）
  - `RedisAdaptor`：统一连接与客户端代理（支持单机与集群、sync/async）。
  - `Proxy`：将 Redis 客户端方法包装为可组合的 `Action`。
- 驱动（`drivers/`）
  - 每种 Redis 类型一个驱动，映射底层命令（如 `StringDriver`、`HashDriver` 等）。
- 模型（`models/`）
  - 基类 `BaseRedisModel` 定义通用能力；各数据结构模型扩展具体操作。
  - 字段元数据通过 `fields(...)` 标注（主键、分片标签、score/hash/member/flag/entry 等）。
- 工具（`utils/`）
  - `Action`：统一封装执行流程，支持 `sequence` 与 `transaction`。
  - 元数据解析、端点解析、驱动选择、日志等。

目录结构（摘录）：

```
src/flamemodel/
  adaptor/         # 连接与客户端代理
  core/            # 键生成器 & 序列化器
  drivers/         # 各 Redis 类型的命令驱动
  models/          # 模型基类与各数据结构模型
  utils/           # Action、元数据解析、工具函数
  main.py          # 框架入口：FlameModel
```

---

## 快速开始

### 环境要求
- Python ≥ 3.10（已兼容 3.10 的 `Self` 回退逻辑）。
- 可用的 Redis 实例（单机或集群）。

### 初始化连接

```python
from src.flamemodel import FlameModel

fm = FlameModel(
    runtime_mode='sync',                 # 或 'async'
    endpoint='redis://localhost:6379/0',# 字符串URL / 连接参数dict / 集群节点list
)
```

`endpoint` 支持三种形式：
- 字符串：`'redis://user:pass@host:port/db'`
- 字典：`{'host': 'localhost', 'port': 6379, 'db': 0}`
- 集群：`[{'host': 'r1', 'port': 6379}, {'host': 'r2', 'port': 6379}]`

### 定义模型与字段元数据

使用 `fields(...)` 为 Pydantic 字段加上 FlameModel 元数据。不同数据结构对必需字段的要求不同（例如 `Hash` 需要一个 `hash_field`，`ZSet` 需要一个 `score_field`，`Geo` 需要 `member/lng/lat`，`BitMap` 需要 `flag`）。

#### String 示例
```python
from src.flamemodel import String, fields

class Counter(String):
    id: str = fields(primary_key=True)
```

```python
c = Counter(id='counter:1')
c.save()           # set
c.incr(2)          # incrby 2
val = Counter.get('counter:1')  # 读取字符串值（反序列化）
```

#### Hash 示例
```python
from src.flamemodel import Hash, fields

class User(Hash):
    id: str = fields(primary_key=True)
    username: str = fields(hash_field=True)  # 作为哈希键中的 field
    email: str = fields()
```

```python
u = User(id='users', username='alice', email='a@x')
u.save()                    # hset('User:users', 'alice', JSON)
User.get('users', 'alice') # hget -> 反序列化为 User
User.values('users')       # hvals -> List[User]
```

#### List 示例
```python
from src.flamemodel import List, fields

class Task(List):
    id: str = fields(primary_key=True)
    title: str = fields()
```

```python
t = Task(id='tasks', title='Do it')
t.append()                # lpush
Task.len('tasks')
Task.get('tasks', 0)
Task.all('tasks')
```

#### Set 示例
```python
from src.flamemodel import Set, fields

class Tag(Set):
    id: str = fields(primary_key=True)
    name: str = fields()
```

```python
tag = Tag(id='tags', name='python')
tag.add()
Tag.members('tags')
Tag.contains('tags', tag)
Tag.union('tags', 'tags2')
```

#### ZSet 示例（需要 `score_field`）
```python
from src.flamemodel import ZSet, fields

class ScoreItem(ZSet):
    id: str = fields(primary_key=True)
    name: str = fields()
    score: float = fields(score_field=True)
```

```python
item = ScoreItem(id='leaderboard', name='alice', score=10)
item.save()
ZSet.top('leaderboard', 10, withscores=True)
item.incr_score(5)
item.get_my_rank(reverse=True)
```

#### Geo 示例（需要 `member_field`、`lng_field`、`lat_field`）
```python
from src.flamemodel import Geo, fields

class Poi(Geo):
    id: str = fields(primary_key=True)
    poi_id: str = fields(member_field=True)
    lng: float = fields(lng_field=True)
    lat: float = fields(lat_field=True)
    name: str = fields()
```

```python
p = Poi(id='city:bj', poi_id='p1', lng=116.397, lat=39.908, name='广场')
p.save()  # 写入 geo + hash
Geo.search_radius('city:bj', 116.397, 39.908, 500, 'm', count=10)
Geo.get_by_member('city:bj', 'p1')
p.delete_self()
```

#### BitMap 示例（需要 `flag`）
```python
from src.flamemodel import BitMap, fields

class Flags(BitMap):
    id: str = fields(primary_key=True)
    is_vip: bool = fields(flag=0)
    is_banned: bool = fields(flag=1)
```

```python
f = Flags(id='user:1', is_vip=True, is_banned=False)
f.save()              # setbit
f.count()             # bitcount 当前实例
Flags.count_by('user:1')
```

#### HyperLogLog 示例
```python
from src.flamemodel import HyperLogLog, fields

class UV(HyperLogLog):
    id: str = fields(primary_key=True)
```

```python
h = UV(id='uv:day:2025-11-26')
h.add('a', 'b', 123)
h.count()
UV.merge_by_pks(['uv:day:2025-11-25', 'uv:day:2025-11-26'])
```

#### Stream 示例（需要 `entry`）
```python
from src.flamemodel import Stream, fields

class Log(Stream):
    id: str = fields(primary_key=True)
    entry_id: str = fields(entry=True)
    message: str = fields()
```

```python
log = Log(id='logs', message='ok')
entry_id = log.add('*')            # xadd 并回填 entry_id
Log.range('logs', '-', '+', count=100)
log.remove()                       # 按自身 entry_id 删除
```

### 运行模式与执行流

- `runtime_mode='sync'`：方法直接返回最终值。
- `runtime_mode='async'`：方法返回协程，需 `await`。

`Action` 通过 `then(...)` 组合处理结果，支持 `sequence`（串行执行聚合）与 `transaction`（事务管道执行）。

### 键生成策略（KeyBuilder）

`DefaultKeyBuilder` 使用冒号分隔的层级键：
- 主键：`ModelName[:shard_tags]:pk`
- 索引：`ModelName[:shard_tags]:idx:field1[:field2...]:value1[:value2...]`
- 唯一：`ModelName[:shard_tags]:uniq:...`
- 外键：`ModelName:pk:fk:field_name`
- 关系：`ModelName:pk:rel:relation_name`

可通过 `FlameModel(..., key_builder_cls=..., key_builder_options=...)` 替换实现。

### 序列化策略（Serializer）

`DefaultSerializer` 基于 Pydantic 2：
- `mode='json'`：`model_dump_json` 输出 JSON（可选 `as_bytes=True` 返回字节）。
- `mode='dict'`：`model_dump(..., mode='python')` 输出字典（用于 `Hash` 字段集场景）。

可通过 `FlameModel(..., serializer_cls=..., serializer_options=...)` 替换实现。

### 适配器（Pythonic 访问）

- `HashAdaptor`：将 `Hash` 映射为 `Mapping`，支持 `model[key]`、`model.keys()`、`model.values()`。
- `ListAdaptor`：将 `List` 映射为序列，支持 `len(model)`、`model[i]`、切片与迭代。

```python
from src.flamemodel.adaptor import HashAdaptor, ListAdaptor

users = HashAdaptor(User, pk='users')
users['alice']      # -> User

tasks = ListAdaptor(Task, pk='tasks')
len(tasks); tasks[0]
```

---

## 异常与约束

- 未标注必需字段（如 `score_field`/`hash_field`/`member_field`/`lng_field`/`lat_field`/`flag`/`entry`）将抛出对应异常。
- 重复设置框架注入对象（Adaptor/Serializer/KeyBuilder）会抛出重复设置异常。
- 未识别的 Redis 数据类型、端点类型会抛出对应异常。

---

## 模型注册机制

`FlameModel` 初始化时会扫描 `BaseRedisModel` 的各子类并自动注册（默认以类名或 `__schema__` 为模型名）。无需手动登记。

---

## 自定义

- 自定义键生成器：实现 `KeyBuilderProtocol` 并在 `FlameModel` 中指定。
- 自定义序列化器：实现 `SerializerProtocol` 并在 `FlameModel` 中指定。
- 自定义命名空间或分片标签：通过 `DefaultKeyBuilder(namespace=...)` 与字段 `shard_tag=True`。

---

## 许可与版本

- 版本：0.0.1
- 作者：surp1us

如需进一步例子或集成建议，请在 Issue 中提出。
