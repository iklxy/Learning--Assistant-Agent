#!/bin/bash

# 测试运行脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    Agent Testing Script                                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 not found. Please install Python3."
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠ Warning: .env file not found"
    echo "  Please create .env file with OPENAI_API_KEY"
    echo ""
fi

# 显示菜单
echo "Select test to run:"
echo "  1) Unit tests (test_agent.py)"
echo "  2) Integration tests (test_agent_workflow.py)"
echo "  3) Run both tests"
echo "  4) Exit"
echo ""
read -p "Enter your choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Running unit tests..."
        echo "════════════════════════════════════════════════════════════════════════════"
        python3 tests/unit/test_agent.py
        ;;
    2)
        echo ""
        echo "Running integration tests..."
        echo "════════════════════════════════════════════════════════════════════════════"
        python3 tests/integration/test_agent_workflow.py
        ;;
    3)
        echo ""
        echo "Running all tests..."
        echo "════════════════════════════════════════════════════════════════════════════"
        echo ""
        echo "[1/2] Unit Tests"
        echo "────────────────────────────────────────────────────────────────────────────"
        python3 tests/unit/test_agent.py
        unit_result=$?

        echo ""
        echo "[2/2] Integration Tests"
        echo "────────────────────────────────────────────────────────────────────────────"
        python3 tests/integration/test_agent_workflow.py
        integration_result=$?

        echo ""
        echo "════════════════════════════════════════════════════════════════════════════"
        echo "Test Results:"
        if [ $unit_result -eq 0 ]; then
            echo "  ✓ Unit tests passed"
        else
            echo "  ✗ Unit tests failed"
        fi

        if [ $integration_result -eq 0 ]; then
            echo "  ✓ Integration tests passed"
        else
            echo "  ✗ Integration tests failed"
        fi
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "Done!"
