# 安装指南

本文档提供详细的安装步骤和配置说明。

## 目录

- [系统要求](#系统要求)
- [快速安装](#快速安装)
- [详细配置](#详细配置)
- [验证安装](#验证安装)
- [常见问题](#常见问题)

---

## 系统要求

### 必需组件

- **Python**: 3.8 或更高版本
- **uv**: Python 包管理器（推荐）或 pip
- **Node.js**: 16.x 或更高版本（用于某些 MCP 服务器）
- **Git**: 用于版本控制

### 可选组件

- **Ollama**: 本地 LLM 引擎（用于项目检测和意图分析）
- **MySQL**: 用于 MCP 数据库工具
- **Redis**: 用于 MCP 缓存工具
- **Docker**: 用于 MCP Docker 工具

### 操作系统支持

- macOS (推荐)
- Linux (Ubuntu 20.04+, Debian 11+)
- Windows (WSL2 推荐)

---

## 快速安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/code-agent.git
cd code-agent
```

### 2. 安装依赖

#### 使用 uv (推荐)

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Python 依赖
uv pip install -r requirements.txt
```

#### 使用 pip

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写必要配置
nano .env
```

### 4. 启动系统

```bash
# 方法 1: 直接启动
python main.py

# 方法 2: 使用 uv
uv run main.py
```

---

## 详细配置

### 环境变量说明

编辑 `.env` 文件，配置以下参数：

#### 基础配置

```env
# Ollama 配置
OLLAMA_MODEL=qwen2.5-coder:7b-instruct-q4_K_M  # 或其他模型

# TTS 配置（可选）
TTS_ENABLED=false
TTS_PROVIDER=openai
TTS_MODEL=tts-1
TTS_VOICE=alloy
```

#### MCP 工具配置

```env
# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASS=your_password_here
MYSQL_DB=your_database

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASS=your_password_here
REDIS_DB=0

# Magic API 配置
MAGIC_API_KEY=your_magic_api_key_here

# Filesystem 配置
FS_ALLOWED_DIR=/path/to/allowed/directory
```

### MCP 服务器配置

`.mcp.json` 文件配置了所有 MCP 服务器。已配置的服务器包括：

| 服务器 | 类型 | 用途 |
|--------|------|------|
| Context7 | npx | 代码库理解和上下文检索 |
| mcp-feedback-enhanced | uvx | 用户交互反馈收集 |
| Sequential Thinking | npx | 复杂问题分解和思考 |
| Shrimp Task Manager | npx | 任务规划和管理 |
| filesystem | npx | 文件系统操作 |
| magic | npx | Magic UI 组件 |
| playwright | npx | Web 应用测试 |
| docker | npx | Docker 容器管理 |
| mysql | uvx | MySQL 数据库操作 |
| magic-ui | npx | Magic UI 组件库 |
| time-mcp | npx | 时间和日期工具 |
| redis-mcp | npx | Redis 缓存操作 |
| chrome-devtools | npx | Chrome 开发者工具 |

**注意**: 大多数 MCP 服务器会自动启动，无需手动配置。敏感凭据通过环境变量引用。

### Ollama 安装与配置

Ollama 用于本地 LLM 推理，提供项目检测和意图分析功能。

#### 安装 Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# 启动 Ollama 服务
ollama serve
```

#### 下载模型

```bash
# 推荐模型: Qwen2.5-Coder 7B
ollama pull qwen2.5-coder:7b-instruct-q4_K_M

# 或其他模型
ollama pull codellama:7b
ollama pull deepseek-coder:6.7b
```

#### 验证 Ollama

```bash
# 测试模型
ollama run qwen2.5-coder:7b-instruct-q4_K_M "Hello, how are you?"
```

### MySQL 配置（可选）

如果使用 MCP MySQL 工具：

```bash
# 安装 MySQL
# macOS
brew install mysql

# Ubuntu
sudo apt install mysql-server

# 启动 MySQL
mysql.server start  # macOS
sudo systemctl start mysql  # Linux

# 创建数据库
mysql -u root -p
CREATE DATABASE your_database;
```

### Redis 配置（可选）

如果使用 MCP Redis 工具：

```bash
# 安装 Redis
# macOS
brew install redis

# Ubuntu
sudo apt install redis-server

# 启动 Redis
redis-server  # macOS
sudo systemctl start redis  # Linux

# 验证 Redis
redis-cli ping  # 应返回 PONG
```

### Docker 配置（可选）

如果使用 MCP Docker 工具：

```bash
# 安装 Docker
# macOS: 下载 Docker Desktop
# Linux
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker  # Linux

# 验证 Docker
docker --version
docker ps
```

---

## 验证安装

### 1. 检查依赖

```bash
# Python 依赖
python -c "import anthropic; print('Anthropic SDK OK')"

# uv
uv --version

# Node.js
node --version
npm --version
```

### 2. 测试 MCP 服务器

```bash
# 测试 Context7
npx @upstash/context7

# 测试 Sequential Thinking
npx @modelcontextprotocol/server-sequential-thinking

# 测试 Filesystem
npx @modelcontextprotocol/server-filesystem
```

### 3. 运行健康检查

```bash
# 运行系统健康检查
python scripts/health_check.py

# 检查 MCP 服务器状态
python scripts/check_mcp_servers.py
```

### 4. 验证 Skills

```bash
# 列出所有 Skills
ls -la .claude/skills/

# 验证 Skill 格式
python scripts/validate_skills.py
```

---

## 常见问题

### MCP 服务器启动失败

**问题**: MCP 服务器无法启动

**解决方案**:
1. 检查 Node.js 版本: `node --version` (需要 16.x+)
2. 清理 npm 缓存: `npm cache clean --force`
3. 重新安装 MCP 服务器: 删除 `node_modules` 并重新运行

### Ollama 连接错误

**问题**: 无法连接到 Ollama 服务

**解决方案**:
1. 检查 Ollama 服务状态: `ps aux | grep ollama`
2. 启动 Ollama: `ollama serve`
3. 检查端口: `lsof -i :11434` (Ollama 默认端口)
4. 验证模型: `ollama list`

### MySQL/Redis 连接失败

**问题**: MCP 工具无法连接数据库

**解决方案**:
1. 检查服务状态: `systemctl status mysql` / `systemctl status redis`
2. 验证凭据: 确认 `.env` 中的用户名、密码、主机、端口正确
3. 测试连接: `mysql -u root -p` / `redis-cli ping`
4. 检查防火墙: 确保端口 3306 (MySQL) / 6379 (Redis) 开放

### 环境变量未生效

**问题**: `.env` 文件中的变量未被读取

**解决方案**:
1. 确认文件名为 `.env` (不是 `.env.example`)
2. 检查文件位置: `.env` 应在项目根目录
3. 重启应用: 修改 `.env` 后需要重启
4. 验证加载: `python -c "import os; print(os.getenv('OLLAMA_MODEL'))"`

### Skills 未加载

**问题**: Skills 无法被识别或使用

**解决方案**:
1. 检查 Skills 目录: `.claude/skills/`
2. 验证文件格式: Skills 应为 `.md` 文件
3. 检查前置元数据: Skills 需要 `name` 和 `description`
4. 重新加载配置

### uv 安装失败

**问题**: 无法安装 uv 包管理器

**解决方案**:
```bash
# 方法 1: 使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 方法 2: 使用 pip
pip install uv

# 方法 3: 使用 brew (macOS)
brew install uv
```

---

## 下一步

- 查看 [Skills 指南](./SKILLS.md) 了解可用的专业能力
- 查看 [MCP 工具文档](./MCP_TOOLS.md) 了解工具集成
- 查看 [Hooks 系统](./HOOKS.md) 了解工作流自定义
- 查看 [故障排除](./TROUBLESHOOTING.md) 解决常见问题

---

**需要帮助?** 提交 [Issue](https://github.com/yourusername/code-agent/issues) 或查看 [讨论区](https://github.com/yourusername/code-agent/discussions)
