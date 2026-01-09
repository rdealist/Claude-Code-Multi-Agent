
---

name: "基础 PRP 模板 v2 - 上下文丰富且具备验证循环"
description: |

---

## 目的

专为 AI Agent 优化的模板，旨在通过提供充足的上下文和自我验证能力，通过迭代优化实现可工作的代码。

## 核心原则

1. **上下文为王 (Context is King)**：包含所有必要的文档、示例和注意事项。
2. **验证循环 (Validation Loops)**：提供 AI 可以运行并修复的可执行测试/代码检查 (Lint)。
3. **信息密度 (Information Dense)**：使用代码库中的关键词和模式。
4. **循序渐进 (Progressive Success)**：从简单开始，验证，然后增强。
5. **全局规则 (Global rules)**：务必遵循 CLAUDE.md 中的所有规则。

---

## 目标

[需要构建什么 - 具体说明最终状态和期望]

## 原因 (Why)

* [商业价值和用户影响]
* [与现有功能的集成]
* [解决了什么问题，为谁解决]

## 内容 (What)

[用户可见的行为和技术要求]

### 成功标准

* [ ] [具体的、可衡量的结果]

## 所有必需的上下文

### 文档与参考资料 (列出实现该功能所需的所有上下文)

```yaml
# 必读 - 将这些包含在你的上下文窗口中
- url: [官方 API 文档 URL]
  why: [你需要的特定部分/方法]
  
- file: [path/to/example.py]
  why: [要遵循的模式，要避免的坑]
  
- doc: [库文档 URL] 
  section: [关于常见陷阱的特定部分]
  critical: [防止常见错误的关键见解]

- docfile: [PRPs/ai_docs/file.md]
  why: [用户粘贴到项目中的文档]

```

### 当前代码库树状图 (在项目根目录运行 `tree` 以获取代码库概览)

```bash


```

### 期望的代码库树状图（包含要添加的文件及文件职责）

```bash


```

### 已知陷阱与库的怪癖 (Gotchas & Quirks)

```python
# 关键：[库名称] 需要 [特定设置]
# 例如：FastAPI 端点需要异步函数 (async functions)
# 例如：此 ORM 不支持批量插入超过 1000 条记录
# 例如：我们使用 pydantic v2 并且...

```

## 实现蓝图

### 数据模型和结构

创建核心数据模型，确保类型安全和一致性。

```python
示例：
 - orm 模型
 - pydantic 模型
 - pydantic schemas
 - pydantic 验证器

```

### 完成 PRP 所需的任务列表（按完成顺序排列）

```yaml
任务 1:
修改 (MODIFY) src/existing_module.py:
  - 查找模式 (FIND pattern): "class OldImplementation"
  - 注入位置 (INJECT after): 在包含 "def __init__" 的行之后
  - 保留 (PRESERVE): 现有的方法签名

创建 (CREATE) src/new_feature.py:
  - 镜像模式 (MIRROR pattern from): 参考 src/similar_feature.py
  - 修改 (MODIFY): 类名和核心逻辑
  - 保持 (KEEP): 错误处理模式一致

...(...)

任务 N:
...

```

### 根据需要的每个任务的伪代码

```python

# 任务 1
# 伪代码包含关键细节，不要写出完整代码
async def new_feature(param: str) -> Result:
    # 模式 (PATTERN): 始终先验证输入 (参考 src/validators.py)
    validated = validate_input(param)  # 抛出 ValidationError
    
    # 陷阱 (GOTCHA): 此库需要连接池
    async with get_connection() as conn:  # 参考 src/db/pool.py
        # 模式 (PATTERN): 使用现有的重试装饰器
        @retry(attempts=3, backoff=exponential)
        async def _inner():
            # 关键 (CRITICAL): 如果 >10 req/sec，API 返回 429
            await rate_limiter.acquire()
            return await external_api.call(validated)
        
        result = await _inner()
    
    # 模式 (PATTERN): 标准化的响应格式
    return format_response(result)  # 参考 src/utils/responses.py

```

### 集成点

```yaml
数据库 (DATABASE):
  - 迁移 (migration): "向 users 表添加 'feature_enabled' 列"
  - 索引 (index): "CREATE INDEX idx_feature_lookup ON users(feature_id)"
  
配置 (CONFIG):
  - 添加到 (add to): config/settings.py
  - 模式 (pattern): "FEATURE_TIMEOUT = int(os.getenv('FEATURE_TIMEOUT', '30'))"
  
路由 (ROUTES):
  - 添加到 (add to): src/api/routes.py  
  - 模式 (pattern): "router.include_router(feature_router, prefix='/feature')"

```

## 验证循环

### 第 1 层：语法与风格

```bash
# 首先运行这些 - 在继续之前修复所有错误
ruff check src/new_feature.py --fix  # 自动修复可能的错误
mypy src/new_feature.py              # 类型检查

# 预期：无错误。如果有错误，阅读错误信息并修复。

```

### 第 2 层：单元测试（每个新功能/文件/函数使用现有的测试模式）

```python
# 创建 (CREATE) test_new_feature.py 并包含这些测试用例：
def test_happy_path():
    """基本功能正常工作"""
    result = new_feature("valid_input")
    assert result.status == "success"

def test_validation_error():
    """无效输入引发 ValidationError"""
    with pytest.raises(ValidationError):
        new_feature("")

def test_external_api_timeout():
    """优雅地处理超时"""
    with mock.patch('external_api.call', side_effect=TimeoutError):
        result = new_feature("valid")
        assert result.status == "error"
        assert "timeout" in result.message

```

```bash
# 运行并迭代直到通过：
uv run pytest test_new_feature.py -v
# 如果失败：阅读错误，理解根本原因，修复代码，重新运行（永远不要为了通过测试而 mock 一切/造假）

```

### 第 3 层：集成测试

```bash
# 启动服务
uv run python -m src.main --dev

# 测试端点
curl -X POST http://localhost:8000/feature \
  -H "Content-Type: application/json" \
  -d '{"param": "test_value"}'

# 预期: {"status": "success", "data": {...}}
# 如果出错: 检查 logs/app.log 中的堆栈跟踪

```

## 最终验证清单

* [ ] 所有测试通过: `uv run pytest tests/ -v`
* [ ] 无代码检查 (Linting) 错误: `uv run ruff check src/`
* [ ] 无类型错误: `uv run mypy src/`
* [ ] 手动测试成功: [具体的 curl/命令]
* [ ] 错误情况处理得当
* [ ] 日志信息丰富但不过于冗长
* [ ] 文档已更新（如果需要）

---

## 要避免的反模式 (Anti-Patterns)

* ❌ 现有模式可行时，不要创建新模式
* ❌ 不要因为“应该能行”就跳过验证
* ❌ 不要忽略失败的测试 - 修复它们
* ❌ 不要在异步上下文中使用同步函数
* ❌ 不要硬编码本应配置的值
* ❌ 不要捕获所有异常 (catch all) - 要具体捕获