import pandas as pd

# Dataset load करणे
data = pd.read_csv("data/food_dataset.csv")


def recommend_food(cuisine, diet, spice_level, meal_type):

    # User preferences नुसार food filter करणे
    recommendations = data[
        (data["cuisine"] == cuisine) &
        (data["diet"] == diet) &
        (data["spice_level"] == spice_level) &
        (data["meal_type"] == meal_type)
    ]

    # Exact match मिळाला नाही तर सर्व foods rating नुसार दाखवणे
    if recommendations.empty:
        recommendations = data.sort_values(
            by="rating",
            ascending=False
        )

    return recommendations.to_dict(orient="records")


# Model Test
if __name__ == "__main__":

    result = recommend_food(
        "Indian",
        "Vegetarian",
        "Spicy",
        "Lunch"
    )

    print(result)