import pandas as pd

def load_flight_data():
    df = pd.read_csv("data/flights.csv")

    return df