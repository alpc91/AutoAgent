import random

canteen_names = ["A食堂", "B食堂", "C食堂"]

# Generate a random rating for the first canteen
def generate_random_rating():
    rating = round(random.uniform(1, 5), 2)  # Random float between 1 and 5
    return {canteen_names[0]: rating}

if __name__ == "__main__":
    random_rating = generate_random_rating()
    print(random_rating)
