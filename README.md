# Code Agent

**为 Claude Code 提供项目感知能力的智能开发框架**

[快速开始](#-快速开始) · [Skills 专家](#-skills-专家) · [MCP 工具](#-mcp-工具集成) · [文档](./docs)

---

## 🎯 核心特性

### 1. 智能项目感知
通过 Hooks 系统自动检测项目类型、框架和依赖，无需手动配置。

### 2. 多个专家 Skills
按技术领域分类的专家智能体，覆盖前端、后端、数据、安全等所有开发环节。

### 3. MCP 工具生态
集成 14+ MCP 工具，包括 Context7、Sequential Thinking、文件系统、数据库等。

### 4. 自动文档维护
强制同步代码与文档，维护 DEVELOPMENT.md、KNOWLEDGE.md、CHANGELOG.md。

---

## 🚀 快速开始

### 前置要求

- **Claude Code** - [下载 Claude Code](https://claude.ai/download)
- **Ollama**（推荐）- 本地 LLM 引擎
- **uv**（推荐）- Python 包管理器

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/Prorise-cool/claude-code-multi-agent.git
cd claude-code-multi-agent

# 2. 安装 Ollama 和模型
# macOS
brew install ollama && ollama pull gemma3:1b

# Windows
winget install Ollama.Ollama
ollama pull gemma3:1b

# 3. 安装 uv
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 4. 配置环境（可选）
cp .env.example .env
# 编辑 .env 填入数据库密码等敏感信息

# 5. 打开 Claude Code
# 选择此目录即可开始使用
```

**验证安装**：在 Claude Code 中输入任意消息，应看到项目类型检测和 Skills 加载提示。

> 📖 **详细安装指南**：[docs/INSTALLATION.md](./docs/INSTALLATION.md)

### 分支策略示例

由于完整配置较为臃肿，可根据开发场景选择对应分支，也可以根据自己项目需求增删mcp工具和skills：

| 分支 | 用途 | 包含的 MCP 工具 |
|------|------|----------------|
| **master** | 完整配置 | 全部 13 个 MCP 服务器 |
| **frontend** | 前端开发 | playwright, magic-ui, chrome-devtools, magic |
| **backend** | 后端开发 | mysql, redis-mcp, docker |
| **algorithm** | 算法研究 | Context7, Sequential Thinking, Shrimp Task Manager |

```bash
# 切换分支
git checkout frontend   # 前端开发
git checkout backend    # 后端开发
git checkout algorithm  # 算法研究
git checkout master     # 完整配置
```

### 📦 配置管理工具（推荐）

使用 **Claude Config Manager** TUI 工具可视化管理配置：

```bash
# 一键安装
./install-ccm.sh

# 使用方式
./ccm              # 启动 TUI 界面
./ccm info         # 查看当前配置（13 MCP, 22 Skills）
./ccm validate     # 验证配置完整性
./ccm create -t ~/new-project -p frontend  # 基于模板创建新项目
./ccm export -o my-config.json             # 导出配置文件
./ccm --help       # 查看所有命令
```

**支持的配置模板：**
| 模板 | MCP 服务器 | Skills | 适用场景 |
|------|-----------|--------|---------|
| `full` | 13 | 22 | 完整开发环境 |
| `frontend` | 9 | 8 | UI/UX 前端开发 |
| `backend` | 8 | 8 | 后端/数据库开发 |
| `algorithm` | 6 | 7 | AI/算法研究 |

---

## 💡 Skills 专家

### 按技术领域分类

#### 🎨 前端开发
- **frontend-specialist** - React、Vue、Next.js 等现代前端框架
- **ui-ux-pro-max** - UI/UX 设计、响应式布局、无障碍设计

#### ⚙️ 后端开发
- **backend-specialist** - Django、FastAPI、Spring Boot 等后端框架
- **language-framework-specialist** - 特定语言和框架的深度专业知识

#### 🗄️ 数据处理
- **data-specialist** - 数据库设计、优化、数据工程和分析

#### 🔒 安全审计
- **security-specialist** - OWASP Top 10、安全审计、风险评估

#### 🏗️ 架构设计
- **architecture-specialist** - 系统设计、微服务架构、技术选型

#### 📋 项目管理
- **project-management-specialist** - 项目管理、任务跟踪、团队协调
- **product-specialist** - 产品规划、需求分析、市场研究

#### ✅ 测试与质量
- **testing-specialist** - 单元测试、集成测试、E2E 测试
- **code-quality-specialist** - 代码审查、性能分析、重构建议

#### 📝 文档与工具
- **documentation-specialist** - 技术文档、API 文档
- **changelog-generator** - 自动生成变更日志
- **mcp-builder** - 创建 MCP 服务器
- **skill-creator** - 创建自定义 Skills
- **file-organizer** - 智能文件组织

#### 🛠️ 其他专家
- **design-specialist** - 视觉设计、品牌一致性
- **marketing-specialist** - 内容营销、增长策略
- **lead-research-assistant** - 潜在客户研究
- **webapp-testing** - Playwright Web 应用测试

### 使用方式

```bash
# 方式 1：直接调用
/backend-specialist 设计用户认证 API

# 方式 2：描述需求，系统自动推荐
"我需要实现用户登录功能"
# 系统会推荐 backend-specialist、security-specialist
```

> 📖 **完整 Skills 文档**：[docs/SKILLS.md](./docs/SKILLS.md)

---

## 🔧 MCP 工具集成

### 核心工具

| 工具 | 功能 | 使用场景 |
|------|------|---------|
| **Context7** | 代码库理解和上下文检索 | 复杂代码依赖分析 |
| **Sequential Thinking** | 复杂问题分解 | 多步骤任务规划 |
| **Shrimp Task Manager** | 任务规划和管理 | 项目任务拆解 |
| **filesystem** | 文件系统操作 | 跨目录文件管理 |
| **mysql** | MySQL 数据库查询 | 数据库操作 |
| **redis-mcp** | Redis 缓存操作 | 缓存管理 |
| **playwright** | Web 自动化测试 | 前端测试 |
| **docker** | Docker 容器管理 | 容器化开发 |
| **magic-ui** | Magic UI 组件库 | UI 组件快速构建 |
| **time-mcp** | 时间处理工具 | 日期时间计算 |

### 配置方式

编辑 `.mcp.json` 和 `.env` 文件：

```bash
# .env 示例
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASS=your_password
REDIS_HOST=localhost
REDIS_PASS=your_redis_password
```

> 📖 **MCP 工具详细配置**：[docs/MCP_TOOLS.md](./docs/MCP_TOOLS.md)

---

## 📚 Hooks 系统

### 自动化工作流

Hooks 在会话生命周期中自动执行，提供智能感知能力：

- **SessionStart** - 会话启动时自动检测项目类型、加载 Skills
- **UserPromptSubmit** - 用户输入时分析意图、推荐工具和 Skills
- **PostToolUse** - 工具使用后强制更新文档

### 文档自动维护

每次代码修改后，系统强制提示更新：
- **DEVELOPMENT.md** - 开发进度、任务状态
- **KNOWLEDGE.md** - 技术决策、代码模式
- **CHANGELOG.md** - 版本记录、功能变更

> 📖 **Hooks 系统原理**：[docs/HOOKS.md](./docs/HOOKS.md)

---

## 📖 使用示例

### 示例 1：自动项目检测

```
用户：打开 Claude Code
系统：✅ 检测到 Python + FastAPI 项目
      ✅ 已加载 27 个 Skills
      ✅ 初始化项目文档
```

### 示例 2：智能意图分析

```
用户：实现用户登录功能
系统：【推荐工具】Sequential Thinking（复杂任务分解）
      【推荐 Skills】/backend-specialist、/security-specialist
      【执行计划】
      1. 设计数据库表结构
      2. 实现认证逻辑
      3. 编写单元测试
      4. 添加安全防护
```

### 示例 3：调用专家 Skills

```
用户：/backend-specialist 设计 RESTful API
系统：以后端专家身份回答，提供：
      ✅ RESTful 资源设计
      ✅ HTTP 方法选择
      ✅ 状态码定义
      ✅ 请求/响应格式
```

---

## 🔒 安全说明

- ✅ **本地运行** - 所有 Hooks 和 Ollama 在本地执行
- ✅ **无网络请求** - 除 Ollama API（本地），不发送外部请求
- ✅ **代码隔离** - 通过 uv 虚拟环境隔离依赖
- ✅ **敏感信息保护** - .env 文件管理凭证，不提交到版本控制

[⬆ 回到顶部](#code-agent)

</div>
