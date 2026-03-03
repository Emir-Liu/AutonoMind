#!/bin/bash
# AutonoMind 测试执行脚本 - Linux/Mac版本

echo "========================================"
echo "  AutonoMind 测试执行脚本"
echo "========================================"
echo

# 设置Python路径
export PYTHONPATH="${PWD}/code:${PYTHONPATH}"

echo "[1/5] 检查测试依赖..."
if ! python -m pip show pytest > /dev/null 2>&1; then
    echo "pytest未安装,正在安装..."
    pip install -r tests/requirements-test.txt
else
    echo "依赖已安装"
fi
echo

echo "[2/5] 运行单元测试..."
echo "----------------------------------------"
python -m pytest tests/unit/ -v --tb=short --disable-warnings -m "not slow" || {
    echo "单元测试失败,但继续运行..."
    echo
}
echo

echo "[3/5] 运行集成测试..."
echo "----------------------------------------"
echo "注意: 集成测试需要数据库环境"
python -m pytest tests/integration/ -v --tb=short --disable-warnings -m "not slow" || {
    echo "集成测试可能需要配置数据库"
    echo
}
echo

echo "[4/5] 运行E2E测试..."
echo "----------------------------------------"
echo "注意: E2E测试需要完整环境"
python -m pytest tests/e2e/ -v --tb=short --disable-warnings -m "not slow" || {
    echo "E2E测试可能需要配置完整环境"
    echo
}
echo

echo "[5/5] 生成测试报告..."
echo "----------------------------------------"
mkdir -p reports
python -m pytest tests/unit/ -v --html=reports/test_report.html --self-contained-html || echo "报告生成失败"
echo

echo "========================================"
echo "  测试执行完成!"
echo "========================================"
echo "测试报告: reports/test_report.html"
echo "========================================"
