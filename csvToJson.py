# pip install pandas
import pandas as pd

# Basic: CSV → pretty JSON (list of objects)
file = "/Users/mdik/CoachAgent-7/Data/activities.csv"
df = pd.read_csv(file)  # add options like sep=";", encoding="utf-8"
df.to_json("activities.json", orient="records", force_ascii=False, indent=2)
