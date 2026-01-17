# MCP 工具完整指南

Model Context Protocol (MCP) 是一个标准化协议，允许 LLM 通过工具与外部服务交互。本文档详细介绍所有已配置的 MCP 服务器。

## 目录

- [什么是 MCP](#什么是-mcp)
- [已配置的 MCP 服务器](#已配置的-mcp-服务器)
- [核心工具](#核心工具)
- [开发工具](#开发工具)
- [数据工具](#数据工具)
- [UI 工具](#ui-工具)
- [自定义配置](#自定义配置)
- [最佳实践](#最佳实践)

---

## 什么是 MCP

MCP (Model Context Protocol) 提供：

- **标准化接口**: 统一的工具调用协议
- **可扩展性**: 轻松添加新工具和服务
- **安全性**: 通过环境变量管理敏感凭据
- **跨平台**: 支持 npx (Node.js) 和 uvx (Python)

### MCP 架构

```
┌─────────────────┐
│   Claude Code   │
└────────┬────────┘
         │
    ┌────▼────┐
    │   MCP   │  (协议层)
    └────┬────┘
         │
    ┌────▼─────────────────────┐
    │  MCP Servers (工具集)    │
    │  - Context7              │
    │  - Sequential Thinking   │
    │  - Filesystem            │
    │  - MySQL                 │
    │  ...                     │
    └──────────────────────────┘
```

---

## 已配置的 MCP 服务器

### 概览表格

| 服务器 | 类型 | 用途 | 需要凭据 |
|--------|------|------|---------|
| [Context7](#context7) | npx | 代码库理解和上下文检索 | ❌ |
| [mcp-feedback-enhanced](#mcp-feedback-enhanced) | uvx | 用户交互反馈收集 | ❌ |
| [Sequential Thinking](#sequential-thinking) | npx | 复杂问题分解和深度思考 | ❌ |
| [Shrimp Task Manager](#shrimp-task-manager) | npx | 任务规划和管理 | ❌ |
| [filesystem](#filesystem) | npx | 文件系统操作 | ⚙️ |
| [magic](#magic) | npx | Magic 服务集成 | ✅ |
| [playwright](#playwright) | npx | Web 应用测试 | ❌ |
| [docker](#docker) | npx | Docker 容器管理 | ❌ |
| [mysql](#mysql) | uvx | MySQL 数据库操作 | ✅ |
| [magic-ui](#magic-ui) | npx | Magic UI 组件库 | ❌ |
| [time-mcp](#time-mcp) | npx | 时间和日期工具 | ❌ |
| [redis-mcp](#redis-mcp) | npx | Redis 缓存操作 | ✅ |
| [chrome-devtools](#chrome-devtools) | npx | Chrome 开发者工具 | ❌ |

**图例**:
- ✅ 必需凭据
- ⚙️ 可选凭据
- ❌ 无需凭据

---

## 核心工具

### Context7

**包名**: `@upstash/context7`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- 代码库语义搜索
- 上下文相关代码检索
- 依赖关系分析
- 代码结构理解

**使用场景**:
```bash
# 场景 1: 查找特定功能实现
"在代码库中查找用户认证相关代码"

# 场景 2: 理解代码依赖
"分析 API 路由的依赖关系"

# 场景 3: 代码库导航
"找到所有使用 Redis 的文件"
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@upstash/context7@0.0.7"]
}
```

**注意事项**:
- 自动索引代码库，首次使用可能较慢
- 支持多种编程语言
- 对大型代码库性能优秀

---

### Sequential Thinking

**包名**: `@modelcontextprotocol/server-sequential-thinking`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- 复杂问题分解
- 逐步推理和思考
- 根因分析
- 决策树构建

**使用场景**:
```bash
# 场景 1: 调试复杂问题
"为什么我的 API 请求会超时？" (系统使用 Sequential Thinking 分析)

# 场景 2: 架构设计
"设计一个高并发的消息队列系统" (系统使用 Sequential Thinking 规划)

# 场景 3: 性能优化
"优化数据库查询性能" (系统使用 Sequential Thinking 分析瓶颈)
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@0.1.3"]
}
```

**优势**:
- 提供结构化思考过程
- 减少跳跃性推理
- 提高复杂问题解决准确率

---

### mcp-feedback-enhanced

**包名**: `mcp-feedback-enhanced`  
**类型**: uvx  
**版本**: 锁定版本

**功能**:
- 用户交互反馈收集
- 实时确认和展示
- 项目进度报告
- 系统信息获取

**使用场景**:
```bash
# 场景 1: 用户确认
系统会自动调用此工具请求用户确认关键操作

# 场景 2: 进度展示
系统完成任务后自动展示成果并等待反馈

# 场景 3: 参数收集
系统需要额外信息时会请求用户输入
```

**配置**:
```json
{
  "command": "uvx",
  "args": ["--from", "mcp-feedback-enhanced@0.2.3", "mcp-feedback-enhanced"]
}
```

**工作流集成**:
- 在 RIPER-5 协议的每个阶段切换时自动调用
- 提问时优先使用
- 空反馈时系统会继续执行

---

### Shrimp Task Manager

**包名**: `@upstash/shrimp-mcp`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- 任务规划和分解
- 进度跟踪
- 任务依赖管理
- 优先级排序

**使用场景**:
```bash
# 场景 1: 复杂任务规划
"实现完整的用户认证系统" (系统使用 Shrimp 分解任务)

# 场景 2: 多步骤执行
系统会创建任务列表并逐步完成

# 场景 3: 进度可视化
用户可以看到每个子任务的完成状态
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@upstash/shrimp-mcp@0.0.2"]
}
```

**与 TodoWrite 的区别**:
- TodoWrite: 轻量级任务跟踪
- Shrimp: 复杂任务规划和依赖管理

---

## 开发工具

### filesystem

**包名**: `@modelcontextprotocol/server-filesystem`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- 文件和目录操作
- 读写文件
- 文件搜索
- 目录遍历

**使用场景**:
```bash
# 场景 1: 文件操作
"创建新文件 src/utils/helper.ts"

# 场景 2: 目录管理
"列出 src/components 下的所有文件"

# 场景 3: 文件搜索
"查找所有包含 'TODO' 的文件"
```

**配置**:
```json
{
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem@0.6.1",
    "${FS_ALLOWED_DIR:-/path/to/your/project}"
  ]
}
```

**安全性**:
- 仅允许访问 `FS_ALLOWED_DIR` 指定的目录
- 默认为项目根目录
- 通过环境变量配置允许的路径

**环境变量**:
```env
FS_ALLOWED_DIR=/path/to/allowed/directory
```

---

### playwright

**包名**: `@executeautomation/playwright-mcp-server`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- Web 应用自动化测试
- 浏览器操作
- 截图和录制
- E2E 测试

**使用场景**:
```bash
# 场景 1: UI 测试
"测试登录流程的表单验证"

# 场景 2: 截图
"访问首页并截图"

# 场景 3: E2E 测试
"完整测试用户注册到登录的流程"
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@executeautomation/playwright-mcp-server@1.1.2"]
}
```

**支持的浏览器**:
- Chromium
- Firefox
- WebKit (Safari)

---

### docker

**包名**: `@modelcontextprotocol/server-docker`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- Docker 容器管理
- Docker Compose 操作
- 容器内命令执行
- 日志查看

**使用场景**:
```bash
# 场景 1: 容器管理
"启动 MySQL 容器"

# 场景 2: 执行命令
"在 app 容器中运行数据库迁移"

# 场景 3: 日志查看
"查看 Redis 容器的最新日志"
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-docker@0.3.1"]
}
```

**前置要求**:
- Docker 已安装并运行
- 当前用户有 Docker 权限

---

### chrome-devtools

**包名**: `@squarednob/server-chrome-devtools`  
**类型**: npx  
**版本**: 最新版本

**功能**:
- Chrome 开发者工具集成
- 控制台日志查看
- 网络请求监控
- 性能分析

**使用场景**:
```bash
# 场景 1: 调试 Web 应用
"查看控制台错误日志"

# 场景 2: 网络分析
"监控 API 请求和响应"

# 场景 3: 性能分析
"分析页面加载性能"
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@squarednob/server-chrome-devtools"]
}
```

---

## 数据工具

### mysql

**包名**: `mcp-server-mysql`  
**类型**: uvx  
**版本**: 锁定版本

**功能**:
- MySQL 数据库连接
- SQL 查询执行
- 数据库操作
- Schema 查看

**使用场景**:
```bash
# 场景 1: 查询数据
"从 users 表中查询所有活跃用户"

# 场景 2: Schema 查看
"显示 orders 表的结构"

# 场景 3: 数据分析
"统计每个月的订单数量"
```

**配置**:
```json
{
  "command": "uvx",
  "args": [
    "--from",
    "mcp-server-mysql@0.6.0",
    "mcp-server-mysql",
    "--host", "${MYSQL_HOST:-localhost}",
    "--port", "${MYSQL_PORT:-3306}",
    "--user", "${MYSQL_USER:-root}",
    "--password", "${MYSQL_PASS}",
    "--database", "${MYSQL_DB:-mysql}"
  ]
}
```

**环境变量**:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASS=your_password_here
MYSQL_DB=your_database
```

**安全性**:
- 密码通过环境变量配置
- 支持只读查询模式
- 避免将凭据写入版本控制

---

### redis-mcp

**包名**: `@upstash/redis-mcp`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- Redis 连接和操作
- 缓存管理
- 键值对操作
- 数据结构操作 (List, Set, Hash)

**使用场景**:
```bash
# 场景 1: 缓存操作
"获取用户 123 的缓存数据"

# 场景 2: 键管理
"列出所有以 'session:' 开头的键"

# 场景 3: 数据结构
"向 'active_users' 集合添加新用户"
```

**配置**:
```json
{
  "command": "npx",
  "args": [
    "-y",
    "@upstash/redis-mcp@0.0.6",
    "${REDIS_HOST:-localhost}",
    "${REDIS_PORT:-6379}",
    "${REDIS_PASS}",
    "${REDIS_DB:-0}"
  ]
}
```

**环境变量**:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASS=your_password_here
REDIS_DB=0
```

**支持的命令**:
- GET, SET, DEL
- LPUSH, RPUSH, LPOP, RPOP
- SADD, SMEMBERS, SREM
- HSET, HGET, HDEL
- KEYS, SCAN, TTL, EXPIRE

---

## UI 工具

### magic

**包名**: `@upstash/magic`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- Magic 服务集成
- API 调用
- 数据处理

**配置**:
```json
{
  "command": "npx",
  "args": [
    "-y",
    "@upstash/magic@0.0.4",
    "${MAGIC_API_KEY}"
  ]
}
```

**环境变量**:
```env
MAGIC_API_KEY=your_magic_api_key_here
```

---

### magic-ui

**包名**: `@upstash/magicui-mcp`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- Magic UI 组件库
- 预构建 UI 组件
- 组件搜索和获取
- 样式和布局

**使用场景**:
```bash
# 场景 1: 获取组件
"获取一个响应式导航栏组件"

# 场景 2: 搜索组件
"搜索所有表单相关组件"

# 场景 3: 组件定制
"获取可定制的按钮组件"
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@upstash/magicui-mcp@0.0.3"]
}
```

**组件类型**:
- 布局组件 (Grid, Flexbox)
- 表单组件 (Input, Select, Button)
- 导航组件 (Navbar, Sidebar)
- 数据展示 (Table, Card, List)

---

### time-mcp

**包名**: `@upstash/time-mcp`  
**类型**: npx  
**版本**: 锁定版本

**功能**:
- 时间和日期工具
- 时区转换
- 日期计算
- 相对时间

**使用场景**:
```bash
# 场景 1: 获取当前时间
"获取当前时间和日期"

# 场景 2: 时区转换
"将 UTC 时间转换为 PST"

# 场景 3: 日期计算
"计算两个日期之间的天数"
```

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@upstash/time-mcp@0.0.2"]
}
```

**支持的操作**:
- 获取当前时间
- 时区转换
- 日期格式化
- 相对时间计算
- 时间戳转换

---

## 自定义配置

### 添加新的 MCP 服务器

编辑 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "npx",  // 或 "uvx"
      "args": [
        "-y",
        "your-package-name@version",
        // 额外参数
      ]
    }
  }
}
```

### 使用环境变量

```json
{
  "mcpServers": {
    "your-server": {
      "command": "npx",
      "args": [
        "-y",
        "your-package",
        "${YOUR_ENV_VAR:-default_value}"
      ]
    }
  }
}
```

**格式**: `${VAR_NAME:-default_value}`
- `VAR_NAME`: 环境变量名称
- `default_value`: 未设置时的默认值

### 锁定版本

**推荐**: 锁定 MCP 服务器版本以确保稳定性

```json
// ✅ 推荐: 锁定版本
"args": ["-y", "@upstash/context7@0.0.7"]

// ❌ 不推荐: 使用 latest
"args": ["-y", "@upstash/context7"]
```

---

## 最佳实践

### 1. 安全管理凭据

```bash
# ✅ 正确: 使用环境变量
MYSQL_PASS=secret123

# ❌ 错误: 硬编码在 .mcp.json
"args": ["--password", "secret123"]
```

### 2. 验证 MCP 服务器

```bash
# 测试 MCP 服务器是否正常工作
npx @upstash/context7@0.0.7 --help
uvx --from mcp-server-mysql@0.6.0 mcp-server-mysql --help
```

### 3. 调试 MCP 问题

```bash
# 查看 MCP 服务器日志
# 日志通常输出到标准错误流

# 手动运行 MCP 服务器测试
npx -y @modelcontextprotocol/server-sequential-thinking@0.1.3
```

### 4. 性能优化

- **延迟加载**: MCP 服务器按需启动，无需预加载
- **版本缓存**: npx 会缓存已下载的包
- **并行执行**: 多个 MCP 工具可以并行调用

### 5. 错误处理

```bash
# 如果 MCP 服务器启动失败:
1. 检查 Node.js/Python 版本
2. 清理缓存: npm cache clean --force
3. 验证环境变量
4. 查看错误日志
```

---

## 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP 服务器列表](https://github.com/modelcontextprotocol/servers)
- [创建自定义 MCP 服务器](./SKILLS.md#mcp-builder)
- [故障排除](./TROUBLESHOOTING.md#mcp-相关问题)

---

**需要帮助?** 查看 [故障排除文档](./TROUBLESHOOTING.md) 或提交 [Issue](https://github.com/yourusername/code-agent/issues)
