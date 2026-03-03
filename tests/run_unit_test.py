#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行单元测试的简化脚本
"""

import sys
import os

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加code目录到Python路径
code_dir = os.path.join(os.path.dirname(__file__), '..', 'code')
sys.path.insert(0, os.path.abspath(code_dir))

print(f"Python Path: {sys.path[:3]}")
print(f"Code Directory: {code_dir}")
print()

# 测试导入
try:
    from core.conversational_learning.interfaces import LearningIntent
    print(f"[OK] 成功导入 LearningIntent")
    print(f"  ADD = {LearningIntent.ADD}")
    print(f"  CORRECT = {LearningIntent.CORRECT}")
    print()

    from core.conversational_learning.interfaces import KnowledgeExtractionResult
    print(f"[OK] 成功导入 KnowledgeExtractionResult")

    # 测试创建对象
    extraction = KnowledgeExtractionResult(
        title="测试标题",
        content="测试知识内容",
        source="test",
        confidence=0.95,
        metadata={"category": "test"}
    )
    print(f"[OK] 成功创建 KnowledgeExtractionResult")
    print(f"  内容: {extraction.content}")
    print(f"  置信度: {extraction.confidence}")
    print()

    from core.conversational_learning.interfaces import LearningIntentResult
    result = LearningIntentResult(
        intent=LearningIntent.ADD,
        confidence=0.90,
        reasoning="测试原因"
    )
    print(f"[OK] 成功创建 LearningIntentResult")
    print(f"  意图: {result.intent}")
    print(f"  置信度: {result.confidence}")
    print()

    print("=" * 50)
    print("所有单元测试导入检查通过!")
    print("=" * 50)

except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

