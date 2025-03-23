import random

canteen_names = ['A食堂', 'B食堂', 'C食堂']

# 为第三个食堂生成一个随机评分
canteen_3_score = random.uniform(0, 10)

print(f"{canteen_names[2]} 的评分为: {canteen_3_score:.2f}")