# 故障排除指南

本文档提供常见问题的解决方案和调试技巧。

## 目录

- [安装相关问题](#安装相关问题)
- [MCP 相关问题](#mcp-相关问题)
- [Hooks 相关问题](#hooks-相关问题)
- [Skills 相关问题](#skills-相关问题)
- [Ollama 相关问题](#ollama-相关问题)
- [数据库相关问题](#数据库相关问题)
- [性能相关问题](#性能相关问题)
- [调试技巧](#调试技巧)

---

## 安装相关问题

### Python 依赖安装失败

**症状**:
```bash
ERROR: Could not find a version that satisfies the requirement anthropic
```

**解决方案**:

```bash
# 1. 检查 Python 版本（需要 3.8+）
python --version

# 2. 升级 pip
pip install --upgrade pip

# 3. 使用 uv（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -r requirements.txt

# 4. 如果仍然失败，检查网络
pip install anthropic --verbose
```

---

### uv 安装失败

**症状**:
```bash
bash: uv: command not found
```

**解决方案**:

```bash
# 方法 1: 官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 方法 2: 使用 pip
pip install uv

# 方法 3: 使用 Homebrew (macOS)
brew install uv

# 方法 4: 手动添加到 PATH
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

---

### Node.js 版本过低

**症状**:
```bash
error: The engine "node" is incompatible with this module
```

**解决方案**:

```bash
# 检查当前版本
node --version

# 使用 nvm 安装新版本
nvm install 18
nvm use 18

# 或使用 Homebrew (macOS)
brew install node@18

# 验证
node --version  # 应该 >= 16.x
```

---

## MCP 相关问题

### MCP 服务器启动失败

**症状**:
```bash
Error: MCP server failed to start: @upstash/context7
```

**原因与解决方案**:

```bash
# 1. 检查 Node.js 版本
node --version  # 需要 16.x+

# 2. 清理 npm 缓存
npm cache clean --force

# 3. 手动测试 MCP 服务器
npx -y @upstash/context7@0.0.7

# 4. 检查 .mcp.json 语法
cat .mcp.json | jq '.'

# 5. 查看详细错误日志
# MCP 服务器错误通常输出到 stderr
```

---

### MCP 服务器无响应

**症状**: MCP 工具调用超时或无响应

**解决方案**:

```bash
# 1. 检查服务器状态
ps aux | grep mcp

# 2. 重启 MCP 服务器（重新启动会话）
# 关闭当前会话并重新开始

# 3. 验证网络连接（对于远程 MCP 服务器）
ping api.upstash.com

# 4. 检查防火墙设置
# 确保 MCP 服务器端口未被阻止
```

---

### 环境变量未生效

**症状**: MCP 服务器无法读取 `.env` 中的凭据

**解决方案**:

```bash
# 1. 确认文件名和位置
ls -la .env  # 应在项目根目录

# 2. 检查文件内容
cat .env

# 3. 验证环境变量语法
# ✅ 正确
MYSQL_PASS=secret123

# ❌ 错误
MYSQL_PASS = secret123  # 不要有空格
MYSQL_PASS="secret123"  # 不要有引号（在 .env 中）

# 4. 重启应用
# 修改 .env 后需要重启

# 5. 验证加载
python -c "import os; print(os.getenv('MYSQL_PASS'))"
```

---

### MCP 版本冲突

**症状**:
```bash
Error: Version mismatch for @upstash/context7
```

**解决方案**:

```bash
# 1. 锁定版本号（推荐）
# 在 .mcp.json 中
"args": ["-y", "@upstash/context7@0.0.7"]  # 明确版本号

# 2. 清理缓存
npm cache clean --force
rm -rf ~/.npm

# 3. 重新安装
npx -y @upstash/context7@0.0.7
```

---

## Hooks 相关问题

### Hook 未执行

**症状**: 配置了 Hook 但未触发

**调试步骤**:

```bash
# 1. 验证配置文件语法
cat .claude/settings.local.json | jq '.hooks'

# 2. 检查 Hook 类型拼写
# ✅ 正确
"SessionStart"
"UserPromptSubmit"
"PostToolUse"

# ❌ 错误
"sessionStart"  # 大小写错误
"PostTooluse"   # 拼写错误

# 3. 测试命令手动执行
bash -c "your hook command"

# 4. 检查权限
chmod +x scripts/your_script.sh

# 5. 查看 Hook 输出
# Hook 输出会显示在对话中
```

---

### Hook 执行失败

**症状**: Hook 返回错误或非零退出码

**解决方案**:

```bash
# 1. 添加错误处理
"args": ["-c", "your_command || true"]  # 忽略错误

# 2. 重定向错误输出
"args": ["-c", "your_command 2>/dev/null || true"]

# 3. 检查命令路径
which prettier
which eslint

# 4. 安装缺失依赖
npm install -g prettier eslint

# 5. 调试模式
"args": ["-c", "set -x; your_command"]  # 显示执行过程
```

---

### Blocking Hook 阻塞流程

**症状**: AI 卡住，无法继续执行

**临时解决方案**:

```json
// 修改 .claude/settings.local.json
{
  "hooks": {
    "PostToolUse": {
      "command": "eslint",
      "args": ["{file_path}"],
      "blocking": false  // 临时改为 false
    }
  }
}
```

**永久解决方案**:

```bash
# 修复 Hook 命令，确保能够成功执行
# 或使用条件执行
"args": ["-c", "[[ -f {file_path} ]] && eslint {file_path} || true"]
```

---

### 变量替换不工作

**症状**: `{prompt}` 或 `{file_path}` 显示为字面量

**原因**: 变量仅在特定 Hook 中可用

**解决方案**:

```json
// ✅ 正确
{
  "UserPromptSubmit": {
    "command": "echo",
    "args": ["{prompt}"]  // UserPromptSubmit 支持 {prompt}
  },
  "PostToolUse": {
    "command": "echo",
    "args": ["{file_path}"]  // PostToolUse 支持 {file_path}
  }
}

// ❌ 错误
{
  "SessionStart": {
    "command": "echo",
    "args": ["{prompt}"]  // SessionStart 不支持 {prompt}
  }
}
```

---

## Skills 相关问题

### Skill 无法识别

**症状**: 调用 Skill 时提示 "Skill not found"

**解决方案**:

```bash
# 1. 检查 Skill 文件存在
ls -la .claude/skills/

# 2. 验证文件名
# 文件名应该是 skill-name.md
# 例如: backend-specialist.md

# 3. 检查文件内容
cat .claude/skills/backend-specialist.md

# 4. 验证前置元数据
# Skill 文件必须以 YAML 前置元数据开始
---
name: backend-specialist
description: 提供后端开发能力
---

# 5. 重新加载配置
# 重启会话
```

---

### Skill 描述未显示

**症状**: Skill 存在但描述为空

**解决方案**:

```markdown
# ✅ 正确的 Skill 格式
---
name: my-skill
description: This is my custom skill
---

# Skill 内容...

# ❌ 错误的格式
name: my-skill
description: Missing YAML front matter

---
```

---

## Ollama 相关问题

### Ollama 无法连接

**症状**:
```bash
Error: Failed to connect to Ollama at http://localhost:11434
```

**解决方案**:

```bash
# 1. 检查 Ollama 服务状态
ps aux | grep ollama

# 2. 启动 Ollama
ollama serve

# 3. 检查端口
lsof -i :11434  # Ollama 默认端口

# 4. 验证连接
curl http://localhost:11434/api/tags

# 5. 重启 Ollama
pkill ollama
ollama serve
```

---

### 模型未找到

**症状**:
```bash
Error: model 'qwen2.5-coder:7b' not found
```

**解决方案**:

```bash
# 1. 列出已下载模型
ollama list

# 2. 下载模型
ollama pull qwen2.5-coder:7b-instruct-q4_K_M

# 3. 验证模型
ollama run qwen2.5-coder:7b-instruct-q4_K_M "test"

# 4. 检查 .env 配置
cat .env | grep OLLAMA_MODEL
```

---

### Ollama 推理缓慢

**症状**: 模型响应时间过长

**解决方案**:

```bash
# 1. 使用更小的量化模型
ollama pull qwen2.5-coder:7b-instruct-q4_K_M  # Q4 量化

# 2. 检查系统资源
htop  # 查看 CPU/内存使用

# 3. 增加 GPU 加速（如果有 GPU）
# Ollama 会自动使用 GPU

# 4. 调整并发设置
export OLLAMA_NUM_PARALLEL=2

# 5. 使用更快的模型
ollama pull codellama:7b  # 更快但可能准确率较低
```

---

## 数据库相关问题

### MySQL 连接失败

**症状**:
```bash
Error: Access denied for user 'root'@'localhost'
```

**解决方案**:

```bash
# 1. 验证凭据
mysql -u root -p
# 输入密码测试连接

# 2. 检查 .env 配置
cat .env | grep MYSQL

# 3. 确认 MySQL 服务运行
# macOS
mysql.server status
mysql.server start

# Linux
sudo systemctl status mysql
sudo systemctl start mysql

# 4. 检查用户权限
mysql -u root -p
SHOW GRANTS FOR 'root'@'localhost';

# 5. 重置密码（如果忘记）
# macOS
mysql.server stop
mysqld_safe --skip-grant-tables &
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

---

### Redis 连接失败

**症状**:
```bash
Error: Could not connect to Redis at localhost:6379
```

**解决方案**:

```bash
# 1. 检查 Redis 服务
redis-cli ping  # 应返回 PONG

# 2. 启动 Redis
# macOS
redis-server

# Linux
sudo systemctl start redis

# 3. 检查端口
lsof -i :6379

# 4. 验证密码（如果设置）
redis-cli -a your_password ping

# 5. 检查 .env 配置
cat .env | grep REDIS
```

---

## 性能相关问题

### 启动缓慢

**症状**: 会话启动时间过长

**优化方案**:

```bash
# 1. 减少 SessionStart Hook 负载
# 避免在 SessionStart 中执行耗时操作

# 2. 优化 MCP 服务器数量
# 禁用不需要的 MCP 服务器（编辑 .mcp.json）

# 3. 使用 SSD
# MCP 服务器频繁读写，SSD 会显著提升性能

# 4. 增加系统资源
# 特别是使用 Ollama 时，需要足够的 RAM
```

---

### 响应缓慢

**症状**: AI 响应时间过长

**优化方案**:

```bash
# 1. 检查 Ollama 性能
# 如果使用 Ollama 进行意图分析，可能拖慢速度

# 2. 简化项目文档
# 减少 CLAUDE.md、DEVELOPMENT.md 等文档的长度

# 3. 减少 Context7 索引范围
# 对于大型代码库，限制索引目录

# 4. 优化 Hook
# 减少 PostToolUse Hook 的执行时间
```

---

### 内存占用过高

**症状**: 系统内存不足

**解决方案**:

```bash
# 1. 使用更小的 Ollama 模型
ollama pull qwen2.5-coder:3b  # 3B 模型更轻量

# 2. 限制 MCP 服务器数量
# 只启用必需的 MCP 服务器

# 3. 关闭不使用的 Ollama 模型
ollama rm unused-model

# 4. 监控内存使用
htop
# 查看哪个进程占用最多内存
```

---

## 调试技巧

### 启用详细日志

```bash
# 1. 查看 MCP 服务器日志
# MCP 错误输出到 stderr

# 2. 测试单个 MCP 服务器
npx -y @upstash/context7@0.0.7 --verbose

# 3. Bash Hook 调试
"args": ["-c", "set -x; your_command"]  # 显示执行过程

# 4. Python 调试
python -v your_script.py  # 详细输出
```

---

### 验证配置文件

```bash
# 1. 验证 JSON 语法
cat .mcp.json | jq '.'
cat .claude/settings.local.json | jq '.'

# 2. 检查环境变量
env | grep MYSQL
env | grep REDIS
env | grep OLLAMA

# 3. 测试 Hook 命令
bash -c "$(jq -r '.hooks.PostToolUse.command' .claude/settings.local.json)"
```

---

### 隔离问题

```bash
# 1. 禁用所有 Hook
# 临时重命名配置文件
mv .claude/settings.local.json .claude/settings.local.json.bak

# 2. 禁用特定 MCP 服务器
# 编辑 .mcp.json，注释掉可疑的服务器

# 3. 测试基础功能
# 确保基本的文件读写操作正常

# 4. 逐步启用
# 逐个启用 Hook/MCP 服务器，找出问题源
```

---

### 收集诊断信息

当需要报告问题时，收集以下信息：

```bash
# 1. 系统信息
uname -a
python --version
node --version
npm --version

# 2. 依赖版本
pip list
npm list -g --depth=0

# 3. 配置文件
cat .mcp.json
cat .env.example  # 不要分享实际的 .env
cat .claude/settings.local.json

# 4. 错误日志
# 复制完整的错误消息

# 5. 重现步骤
# 详细描述如何触发问题
```

---

## 常见错误速查

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `command not found: uv` | uv 未安装或不在 PATH | 安装 uv 并添加到 PATH |
| `MCP server failed to start` | Node.js 版本过低 | 升级 Node.js 到 16.x+ |
| `Access denied` (MySQL) | 密码错误或权限不足 | 检查 .env 中的凭据 |
| `Could not connect to Redis` | Redis 未运行 | 启动 Redis 服务 |
| `Ollama connection failed` | Ollama 未运行 | 启动 `ollama serve` |
| `Hook execution failed` | 命令返回非零退出码 | 添加 `|| true` 忽略错误 |
| `Skill not found` | Skill 文件缺失或格式错误 | 检查文件名和 YAML 前置元数据 |
| `Version mismatch` | MCP 服务器版本冲突 | 锁定版本号，清理缓存 |

---

## 获取帮助

### 社区资源

- **GitHub Issues**: [提交问题](https://github.com/yourusername/code-agent/issues)
- **讨论区**: [参与讨论](https://github.com/yourusername/code-agent/discussions)
- **MCP 官方文档**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Claude Code 文档**: [docs.anthropic.com/claude-code](https://docs.anthropic.com/claude-code)

### 报告 Bug

提交 Issue 时请包含：

1. **问题描述**: 清晰描述问题
2. **重现步骤**: 如何触发问题
3. **期望行为**: 应该发生什么
4. **实际行为**: 实际发生了什么
5. **环境信息**: 操作系统、Python 版本、Node.js 版本
6. **错误日志**: 完整的错误消息
7. **配置文件**: 相关的配置（去除敏感信息）

---

**还有问题?** 查看 [安装指南](./INSTALLATION.md)、[MCP 工具文档](./MCP_TOOLS.md) 或 [Hooks 系统文档](./HOOKS.md)
