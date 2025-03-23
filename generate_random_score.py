import random

canteen_names = ["A食堂", "B食堂", "C食堂"]

# 为第二个食堂生成一个随机评分
def generate_random_score():
    score = random.randint(1, 5)
    print(f"为{canteen_names[1]}生成的随机评分是：{score}")

if __name__ == "__main__":
    generate_random_score()
