import pandas as pd

# 读取Excel文件
df = pd.read_excel('游戏评判维度表 20260313.xlsx')

# 打印所有列名
print("列名：", df.columns.tolist())
print("\n数据预览：")
print(df.head())

# 保存为CSV方便查看
df.to_csv('游戏评判维度表.csv', index=False, encoding='utf-8-sig')
print("\n已保存为CSV文件：游戏评判维度表.csv")
