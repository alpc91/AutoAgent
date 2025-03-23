import random

canteen_names = ['A食堂', 'B食堂', 'C食堂']

# 为第二个食堂生成一个随机评分
second_canteen = canteen_names[1]
random_rating = random.randint(1, 5)

print(f'{second_canteen} 的随机评分为: {random_rating}')