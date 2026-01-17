#!/bin/bash
# Claude Config Manager - Installation Script
# Usage: ./install-ccm.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_DIR="$SCRIPT_DIR/tools/claude-config-manager"
VENV_DIR="$TOOL_DIR/.venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╭─────────────────────────────────────────────╮${NC}"
echo -e "${BLUE}│  Claude Config Manager - 安装程序           │${NC}"
echo -e "${BLUE}╰─────────────────────────────────────────────╯${NC}"
echo

# Check Python version
echo -e "${YELLOW}检查 Python 版本...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗ 需要 Python 3.10+，当前版本: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if uv is available
USE_UV=false
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓ 检测到 uv，将使用 uv 进行安装（更快）${NC}"
    USE_UV=true
else
    echo -e "${YELLOW}⚠ 未检测到 uv，将使用 pip 进行安装${NC}"
    echo -e "${YELLOW}  提示: 安装 uv 可获得更快的安装速度: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
fi

# Create virtual environment
echo
echo -e "${YELLOW}创建虚拟环境...${NC}"
cd "$TOOL_DIR"

if [ "$USE_UV" = true ]; then
    uv venv "$VENV_DIR"
else
    python3 -m venv "$VENV_DIR"
fi
echo -e "${GREEN}✓ 虚拟环境创建完成${NC}"

# Activate and install
echo
echo -e "${YELLOW}安装依赖...${NC}"
source "$VENV_DIR/bin/activate"

if [ "$USE_UV" = true ]; then
    uv pip install -e .
else
    pip install --upgrade pip
    pip install -e .
fi
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# Verify installation
echo
echo -e "${YELLOW}验证安装...${NC}"
if ccm --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ccm 命令可用${NC}"
else
    echo -e "${RED}✗ ccm 命令不可用${NC}"
    exit 1
fi

# Set execute permission for launch script
chmod +x "$SCRIPT_DIR/ccm"

echo
echo -e "${GREEN}╭─────────────────────────────────────────────╮${NC}"
echo -e "${GREEN}│  ✓ 安装完成！                               │${NC}"
echo -e "${GREEN}╰─────────────────────────────────────────────╯${NC}"
echo
echo -e "使用方法:"
echo -e "  ${BLUE}./ccm${NC}              启动 TUI 界面"
echo -e "  ${BLUE}./ccm info${NC}         查看当前配置"
echo -e "  ${BLUE}./ccm validate${NC}     验证配置完整性"
echo -e "  ${BLUE}./ccm --help${NC}       查看所有命令"
echo
echo -e "或者激活虚拟环境后直接使用 ccm:"
echo -e "  ${BLUE}source tools/claude-config-manager/.venv/bin/activate${NC}"
echo -e "  ${BLUE}ccm${NC}"
