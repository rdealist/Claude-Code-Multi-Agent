# Hooks 系统指南

Hooks 是 Code Agent 的工作流自定义系统，允许在特定事件发生时自动执行 Shell 命令。

## 目录

- [什么是 Hooks](#什么是-hooks)
- [Hook 类型](#hook-类型)
- [配置 Hooks](#配置-hooks)
- [实际应用场景](#实际应用场景)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

---

## 什么是 Hooks

Hooks 提供事件驱动的自动化能力：

- **自动化工作流**: 在特定时机自动执行命令
- **上下文注入**: 向 AI 提供额外的上下文信息
- **质量门控**: 阻止不符合规范的操作
- **集成外部工具**: 连接 linters、formatters、测试框架等

### Hook 执行流程

```
┌─────────────┐
│  事件触发    │  (SessionStart, ToolUse, etc.)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  执行 Hook  │  (Shell 命令)
└──────┬──────┘
       │
       ├─── Success ──→ 继续执行
       │
       └─── Failure ──→ 阻止/提示
```

---

## Hook 类型

### 1. SessionStart

**触发时机**: 每次会话开始时

**用途**:
- 提供项目上下文信息
- 注入项目配置
- 加载环境变量
- 显示项目状态

**示例配置**:
```json
{
  "hooks": {
    "SessionStart": {
      "command": "bash",
      "args": ["-c", "cat project_summary.txt"],
      "blocking": false
    }
  }
}
```

**实际应用**:

```bash
# 1. 显示项目信息
{
  "SessionStart": {
    "command": "bash",
    "args": ["-c", "echo 'Project: MyApp | Branch: $(git branch --show-current)'"]
  }
}

# 2. 检查依赖更新
{
  "SessionStart": {
    "command": "npm",
    "args": ["outdated"]
  }
}

# 3. 加载项目配置
{
  "SessionStart": {
    "command": "bash",
    "args": ["-c", "cat .project/context.md"]
  }
}
```

**输出处理**:
- 输出内容会作为系统消息注入到对话
- AI 可以看到并使用这些信息
- 适合提供项目背景、规范、约定等

---

### 2. UserPromptSubmit

**触发时机**: 用户提交消息后，AI 处理前

**用途**:
- 分析用户意图
- 提供上下文相关建议
- 注入实时信息
- 预处理用户输入

**示例配置**:
```json
{
  "hooks": {
    "UserPromptSubmit": {
      "command": "python",
      "args": ["scripts/analyze_intent.py", "{prompt}"],
      "blocking": false
    }
  }
}
```

**实际应用**:

```bash
# 1. 意图分析
{
  "UserPromptSubmit": {
    "command": "bash",
    "args": ["-c", "ollama run qwen2.5-coder:7b \"Analyze intent: {prompt}\""]
  }
}

# 2. 提供相关文档
{
  "UserPromptSubmit": {
    "command": "bash",
    "args": ["-c", "grep -r '{prompt}' docs/ | head -5"]
  }
}

# 3. 检查项目状态
{
  "UserPromptSubmit": {
    "command": "git",
    "args": ["status", "--short"]
  }
}
```

**变量替换**:
- `{prompt}`: 用户输入的消息内容
- Hook 可以访问并处理用户输入

---

### 3. PostToolUse

**触发时机**: AI 使用工具后

**用途**:
- 验证工具输出
- 执行后续操作
- 代码质量检查
- 自动格式化

**示例配置**:
```json
{
  "hooks": {
    "PostToolUse": {
      "command": "bash",
      "args": ["-c", "npm run lint"],
      "blocking": true
    }
  }
}
```

**实际应用**:

```bash
# 1. 代码格式化 (Write 工具后)
{
  "PostToolUse": {
    "command": "prettier",
    "args": ["--write", "{file_path}"],
    "tools": ["Write"]
  }
}

# 2. 代码检查 (Edit 工具后)
{
  "PostToolUse": {
    "command": "eslint",
    "args": ["{file_path}", "--fix"],
    "tools": ["Edit"],
    "blocking": true
  }
}

# 3. 运行测试 (Write/Edit 后)
{
  "PostToolUse": {
    "command": "npm",
    "args": ["test", "--", "{file_path}"],
    "tools": ["Write", "Edit"],
    "blocking": true
  }
}
```

**工具过滤**:
- `tools` 字段指定触发 Hook 的工具
- 不指定则对所有工具生效
- 可以精确控制 Hook 执行时机

---

## 配置 Hooks

### 配置文件位置

- **全局配置**: `~/.claude/settings.json`
- **项目配置**: `.claude/settings.local.json`

项目配置会覆盖全局配置。

### Hook 配置结构

```json
{
  "hooks": {
    "HookType": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "blocking": false,
      "tools": ["ToolName1", "ToolName2"]
    }
  }
}
```

**字段说明**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `command` | string | ✅ | 要执行的命令 |
| `args` | array | ❌ | 命令参数 |
| `blocking` | boolean | ❌ | 是否阻塞（默认 false） |
| `tools` | array | ❌ | 触发的工具列表（仅 PostToolUse） |

### Blocking 模式

**非阻塞 (blocking: false)**:
- Hook 失败不影响主流程
- 输出作为上下文注入
- 适合信息提供、建议

**阻塞 (blocking: true)**:
- Hook 失败会阻止操作
- 必须成功才能继续
- 适合质量门控、验证

---

## 实际应用场景

### 场景 1: 自动代码格式化

**目标**: 每次修改代码后自动格式化

```json
{
  "hooks": {
    "PostToolUse": {
      "command": "bash",
      "args": ["-c", "prettier --write {file_path} 2>/dev/null || true"],
      "tools": ["Write", "Edit"],
      "blocking": false
    }
  }
}
```

**工作流**:
1. AI 使用 Write/Edit 修改文件
2. Hook 自动运行 Prettier
3. 代码格式化完成
4. AI 继续执行

---

### 场景 2: 代码质量门控

**目标**: 阻止不符合 ESLint 规范的代码

```json
{
  "hooks": {
    "PostToolUse": {
      "command": "eslint",
      "args": ["{file_path}"],
      "tools": ["Write", "Edit"],
      "blocking": true
    }
  }
}
```

**工作流**:
1. AI 写入代码
2. ESLint 检查代码
3. 如果有错误 → 阻止操作，AI 收到错误信息并修复
4. 如果通过 → 继续执行

---

### 场景 3: 自动运行测试

**目标**: 修改代码后自动运行相关测试

```json
{
  "hooks": {
    "PostToolUse": {
      "command": "bash",
      "args": ["-c", "npm test -- $(echo {file_path} | sed 's/src/tests/; s/.ts/.test.ts/')"],
      "tools": ["Write", "Edit"],
      "blocking": true
    }
  }
}
```

**工作流**:
1. AI 修改 `src/utils/helper.ts`
2. Hook 运行 `tests/utils/helper.test.ts`
3. 测试失败 → AI 收到错误并修复
4. 测试通过 → 继续执行

---

### 场景 4: 项目上下文注入

**目标**: 每次会话提供项目规范

```json
{
  "hooks": {
    "SessionStart": {
      "command": "bash",
      "args": ["-c", "cat docs/CODING_STANDARDS.md docs/PROJECT_CONVENTIONS.md"]
    }
  }
}
```

**效果**:
- AI 自动了解项目编码规范
- 遵循项目约定
- 减少人工说明

---

### 场景 5: Git 提交检查

**目标**: 确保提交前代码通过所有检查

```json
{
  "hooks": {
    "PostToolUse": {
      "command": "bash",
      "args": ["-c", "npm run lint && npm test"],
      "tools": ["Bash"],
      "blocking": true
    }
  }
}
```

当 AI 执行 `git commit` 时，Hook 会先运行 lint 和 test。

---

### 场景 6: Ollama 意图分析

**目标**: 使用本地 LLM 分析用户意图

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "command": "bash",
      "args": [
        "-c",
        "ollama run qwen2.5-coder:7b \"User request: {prompt}. Identify: 1) Intent (code/debug/question), 2) Affected files, 3) Complexity (simple/medium/complex). Format: Intent: X | Files: Y | Complexity: Z\""
      ],
      "blocking": false
    }
  }
}
```

**效果**:
- AI 获得意图分析结果
- 更好地规划任务
- 选择合适的策略

---

## 最佳实践

### 1. 错误处理

```bash
# ✅ 推荐: 优雅处理错误
"args": ["-c", "prettier --write {file_path} 2>/dev/null || true"]

# ❌ 不推荐: 让错误中断流程（除非是质量门控）
"args": ["-c", "prettier --write {file_path}"]
```

### 2. 性能优化

```bash
# ✅ 推荐: 只检查修改的文件
"args": ["{file_path}"]

# ❌ 不推荐: 检查所有文件（慢）
"args": ["src/**/*.ts"]
```

### 3. 合理使用 Blocking

```bash
# ✅ Blocking: 质量门控
{
  "blocking": true,  // 代码必须通过检查
  "command": "eslint"
}

# ✅ Non-blocking: 信息提供
{
  "blocking": false,  // 失败也不影响流程
  "command": "cat project_context.md"
}
```

### 4. 组合使用多个 Hooks

```json
{
  "hooks": {
    "SessionStart": {
      "command": "bash",
      "args": ["-c", "cat docs/CONVENTIONS.md"]
    },
    "PostToolUse": {
      "command": "prettier",
      "args": ["--write", "{file_path}"],
      "tools": ["Write", "Edit"]
    }
  }
}
```

### 5. 调试 Hook

```bash
# 测试 Hook 命令
bash -c "prettier --write src/index.ts"

# 查看 Hook 输出
# Hook 输出会显示在对话中

# 验证 Hook 配置
cat .claude/settings.local.json | jq '.hooks'
```

---

## 故障排除

### Hook 未执行

**可能原因**:
1. 配置文件语法错误
2. 命令路径不正确
3. 工具过滤不匹配

**解决方案**:
```bash
# 验证 JSON 语法
cat .claude/settings.local.json | jq '.'

# 测试命令
which prettier  # 确认命令存在
prettier --version

# 检查工具名称
# 确保 "tools" 字段中的名称正确（Write, Edit, Bash 等）
```

### Hook 执行失败

**可能原因**:
1. 命令返回非零退出码
2. 权限不足
3. 依赖缺失

**解决方案**:
```bash
# 添加错误处理
"args": ["-c", "your_command || true"]

# 检查权限
chmod +x scripts/your_script.sh

# 安装依赖
npm install -g prettier eslint
```

### Blocking Hook 阻塞流程

**现象**: AI 无法继续执行，卡住

**解决方案**:
```json
// 临时禁用 blocking
{
  "PostToolUse": {
    "command": "eslint",
    "args": ["{file_path}"],
    "blocking": false  // 改为 false
  }
}
```

### 变量替换不工作

**问题**: `{prompt}` 或 `{file_path}` 未被替换

**原因**: 变量仅在特定 Hook 中可用
- `{prompt}`: 仅 UserPromptSubmit
- `{file_path}`: 仅 PostToolUse

**解决方案**:
```bash
# 确保在正确的 Hook 中使用正确的变量
{
  "UserPromptSubmit": {
    "command": "echo",
    "args": ["{prompt}"]  # ✅ 正确
  },
  "PostToolUse": {
    "command": "echo",
    "args": ["{file_path}"]  # ✅ 正确
  }
}
```

---

## 高级技巧

### 1. 条件执行

```bash
# 仅对 TypeScript 文件运行 ESLint
{
  "PostToolUse": {
    "command": "bash",
    "args": [
      "-c",
      "[[ {file_path} == *.ts ]] && eslint {file_path} || true"
    ],
    "tools": ["Write", "Edit"]
  }
}
```

### 2. 链式 Hook

```bash
# 格式化 → 检查 → 测试
{
  "PostToolUse": {
    "command": "bash",
    "args": [
      "-c",
      "prettier --write {file_path} && eslint {file_path} && npm test"
    ],
    "tools": ["Write", "Edit"],
    "blocking": true
  }
}
```

### 3. 多工具触发

```bash
# 对不同工具执行不同操作
{
  "PostToolUse": {
    "command": "bash",
    "args": [
      "-c",
      "case {tool} in Write|Edit) prettier --write {file_path};; Bash) echo 'Command executed';; esac"
    ]
  }
}
```

---

## 示例配置合集

### 前端开发环境

```json
{
  "hooks": {
    "SessionStart": {
      "command": "bash",
      "args": ["-c", "echo 'Project: $(npm run env | grep npm_package_name)' && git status -sb"]
    },
    "PostToolUse": {
      "command": "bash",
      "args": ["-c", "prettier --write {file_path} && eslint {file_path}"],
      "tools": ["Write", "Edit"],
      "blocking": true
    }
  }
}
```

### Python 开发环境

```json
{
  "hooks": {
    "SessionStart": {
      "command": "bash",
      "args": ["-c", "python --version && pip list | grep -E '(django|flask|fastapi)'"]
    },
    "PostToolUse": {
      "command": "bash",
      "args": ["-c", "black {file_path} && pylint {file_path}"],
      "tools": ["Write", "Edit"],
      "blocking": true
    }
  }
}
```

### 测试驱动开发 (TDD)

```json
{
  "hooks": {
    "PostToolUse": {
      "command": "bash",
      "args": ["-c", "npm test -- {file_path}"],
      "tools": ["Write", "Edit"],
      "blocking": true
    }
  }
}
```

---

## 相关资源

- [配置文件位置](./INSTALLATION.md#配置-hooks)
- [常见工具命令](./MCP_TOOLS.md)
- [故障排除](./TROUBLESHOOTING.md#hooks-相关问题)

---

**需要帮助?** 提交 [Issue](https://github.com/yourusername/code-agent/issues) 或查看 [讨论区](https://github.com/yourusername/code-agent/discussions)
