"""
测试pandas导入
"""
print("开始测试pandas导入...")

try:
    import pandas as pd
    print("✓ pandas导入成功")
    print(f"  pandas版本: {pd.__version__}")
    PANDAS_AVAILABLE = True
except ImportError as e:
    print("✗ pandas导入失败（这是正常的，如果不需要Excel/CSV导入）")
    print(f"  错误: {e}")
    PANDAS_AVAILABLE = False
    pd = None
except Exception as e:
    print(f"✗ pandas导入时发生其他错误: {e}")
    import traceback
    traceback.print_exc()
    PANDAS_AVAILABLE = False
    pd = None

print(f"\nPANDAS_AVAILABLE = {PANDAS_AVAILABLE}")

if PANDAS_AVAILABLE:
    print("\n测试pandas基本功能...")
    try:
        import io
        test_data = "name,age\n张三,30\n李四,25"
        df = pd.read_csv(io.StringIO(test_data))
        print("✓ pandas CSV读取测试成功")
        print(df)
    except Exception as e:
        print(f"✗ pandas功能测试失败: {e}")
else:
    print("\n跳过pandas功能测试（pandas未安装）")

print("\n测试完成！")
