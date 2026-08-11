import pandas as pd

# Dataset load
data = pd.read_csv("data/food_dataset.csv")


# -----------------------------------------
# FOOD NAME COLUMN FINDER
# -----------------------------------------

def get_food_name_column():

    possible_columns = [
        "name",
        "food_name",
        "food",
        "Food",
        "Food_Name",
        "dish",
        "Dish",
        "item",
        "Item"
    ]

    for column in possible_columns:
        if column in data.columns:
            return column

    return None


# -----------------------------------------
# OLD RECOMMENDATION FUNCTION
# -----------------------------------------

def recommend_food(cuisine, diet, spice_level, meal_type):

    recommendations = data[
        (data["cuisine"] == cuisine) &
        (data["diet"] == diet) &
        (data["spice_level"] == spice_level) &
        (data["meal_type"] == meal_type)
    ]

    # Exact match नसेल तर rating नुसार foods
    if recommendations.empty:

        recommendations = data.sort_values(
            by="rating",
            ascending=False
        )

    return recommendations.to_dict(
        orient="records"
    )


# -----------------------------------------
# NEW SEARCH FUNCTION
# -----------------------------------------

def search_food(search_text):

    search_text = search_text.strip().lower()

    # Empty search
    if not search_text:

        results = data.sort_values(
            by="rating",
            ascending=False
        )

        return results.to_dict(
            orient="records"
        )


    # Food name column शोधणे
    food_column = get_food_name_column()


    # Food name column मिळाला
    if food_column:

        results = data[
            data[food_column]
            .astype(str)
            .str.lower()
            .str.contains(
                search_text,
                na=False
            )
        ]

    else:

        # Food name column नसेल तर
        # सर्व text columns मध्ये search

        text_columns = data.select_dtypes(
            include=["object"]
        ).columns

        results = data.iloc[0:0]

        for column in text_columns:

            matching_rows = data[
                data[column]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
            ]

            results = pd.concat(
                [results, matching_rows]
            )

        # Duplicate remove
        results = results.drop_duplicates()


    # Rating नुसार sort
    if "rating" in results.columns:

        results = results.sort_values(
            by="rating",
            ascending=False
        )


    return results.to_dict(
        orient="records"
    )


# -----------------------------------------
# TEST
# -----------------------------------------

if __name__ == "__main__":

    print("Dataset Columns:")
    print(data.columns.tolist())


    print("\nSearch Test:")

    result = search_food("pizza")

    print(result)
    