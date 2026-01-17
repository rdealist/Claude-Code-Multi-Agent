---
name: "基础 PRP 模板 v2 - 上下文丰富且具备验证循环"
description: "专为 AI Agent 优化：充足上下文 + 自我验证 + 迭代优化"
---

## 核心原则

1. **充足上下文**：包含所有必要文档、示例和注意事项
2. **验证循环**：提供可执行测试和代码检查，AI 可自行修复
3. **信息密度**：使用代码库关键词和模式
4. **循序渐进**：从简单开始，验证后增强
5. **全局规则**：遵循 CLAUDE.md 所有规则

---

## 目标

[明确说明构建内容 - 最终状态和期望结果]

## 原因

* [商业价值和用户影响]
* [与现有系统的集成方式]
* [解决的问题及受益者]

## 内容

[用户可见行为和技术实现要求]

**成功标准：**
* [ ] [具体可衡量的结果指标]

## 必需上下文

### 文档与参考资料

```yaml
# 必读 - 包含在上下文窗口中
- url: [官方 API 文档]
  why: [需要的特定部分/方法]
  
- file: [path/to/example.py]
  why: [参考模式/需避免的陷阱]
  
- doc: [库文档 URL] 
  section: [关键章节或常见陷阱]
  
- docfile: [PRPs/ai_docs/file.md]
  why: [用户提供的补充文档]
```

### 代码库结构

运行 `tree -L 3 -I 'node_modules|__pycache__|.git'` 获取项目结构,并说明需新增文件及其职责。

### 已知陷阱与库特性

```python
# [库名称] 特定要求：[配置/用法]
# 示例：FastAPI 端点必须使用 async 函数
# 示例：此 ORM 批量插入限制 1000 条/次
# 示例：项目使用 pydantic v2,注意迁移差异
```

## 实现蓝图

### 数据模型设计

```python
# 定义核心数据结构,确保类型安全
# 包含：ORM 模型、Pydantic 模型、Schema、自定义验证器
```

### 任务分解（按执行顺序）

```yaml
Task 1:
  MODIFY: src/existing_module.py
    - FIND: "class OldImplementation"
    - INJECT_AFTER: "def __init__"
    - PRESERVE: 现有方法签名

  CREATE: src/new_feature.py
    - MIRROR_FROM: src/similar_feature.py
    - MODIFY: 类名和核心逻辑
    - KEEP: 错误处理模式

Task N:
  ...
```

### 关键实现伪代码

```python
# Task 1: [功能描述]
async def new_feature(param: str) -> Result:
    # PATTERN: 输入验证优先 (参考 src/validators.py)
    validated = validate_input(param)
    
    # GOTCHA: 需使用连接池
    async with get_connection() as conn:
        # PATTERN: 复用现有重试装饰器
        @retry(attempts=3)
        async def _inner():
            # CRITICAL: API 限流 10 req/sec,超限返回 429
            await rate_limiter.acquire()
            return await external_api.call(validated)
        
        result = await _inner()
    
    # PATTERN: 统一响应格式
    return format_response(result)
```

### 集成点

```yaml
DATABASE:
  - migration: "ALTER TABLE users ADD COLUMN feature_enabled BOOLEAN"
  - index: "CREATE INDEX idx_feature_lookup ON users(feature_id)"
  
CONFIG:
  - add_to: config/settings.py
  - pattern: "FEATURE_TIMEOUT = int(os.getenv('FEATURE_TIMEOUT', '30'))"
  
ROUTES:
  - add_to: src/api/routes.py  
  - pattern: "router.include_router(feature_router, prefix='/feature')"
```

## 验证循环

### 第 1 层：静态分析

```bash
ruff check src/new_feature.py --fix  # Lint 并自动修复
mypy src/new_feature.py              # 类型检查
# 预期无错误,有错误时分析原因并修复
```

### 第 2 层：单元测试

```python
# test_new_feature.py
def test_happy_path():
    """验证基本功能正常执行"""
    result = new_feature("valid_input")
    assert result.status == "success"

def test_validation_error():
    """验证输入校验机制"""
    with pytest.raises(ValidationError):
        new_feature("")

def test_external_api_timeout():
    """验证超时异常处理"""
    with mock.patch('external_api.call', side_effect=TimeoutError):
        result = new_feature("valid")
        assert result.status == "error"
        assert "timeout" in result.message
```

```bash
uv run pytest test_new_feature.py -v
# 失败时流程：分析错误 → 定位根因 → 修复代码 → 重新测试
```

### 第 3 层：集成测试

```bash
# 启动开发服务器
uv run python -m src.main --dev

# 端点测试
curl -X POST http://localhost:8000/feature \
  -H "Content-Type: application/json" \
  -d '{"param": "test_value"}'

# 预期响应: {"status": "success", "data": {...}}
# 异常排查: 检查 logs/app.log
```

## 最终验证清单

* [ ] 单元测试通过：`uv run pytest tests/ -v`
* [ ] 静态检查通过：`uv run ruff check src/`
* [ ] 类型检查通过：`uv run mypy src/`
* [ ] 手动测试通过：[具体测试命令]
* [ ] 异常场景处理完善
* [ ] 日志记录适度且有效
* [ ] 相关文档已同步更新

---

## 反模式规避清单

* ❌ 已有可用模式时避免重复造轮子
* ❌ 禁止跳过验证环节
* ❌ 失败测试必须修复,不得忽略
* ❌ 异步上下文禁用同步函数
* ❌ 避免硬编码,使用配置管理
* ❌ 异常捕获需具体化,避免泛捕获
