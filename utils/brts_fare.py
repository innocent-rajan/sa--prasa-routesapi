import pandas as pd
import pickle

b1_up = pd.read_csv('../../../../Documents/BRTS Fare/B1UP - B1UP-Table 1.csv')
b1_down = pd.read_csv('../../../../Documents/BRTS Fare/B1DOWN - B1DOWN-Table 1.csv')
b1up = b1_up.drop(columns=['Name (B1UP)'])
b1down = b1_down.drop(columns=['Name (B1DOWN)'])

b1up = b1up.fillna(0)
b2down = b1down.fillna(0)

b1up_dict_named = {
    (int(b1up.iloc[row, 0]), int(b1up.columns[col])): int(b1up.iloc[row, col])
    for row in range(b1up.shape[0])
    for col in range(1, b1up.shape[1])
}

b1down_dict_named = {
    (int(b2down.iloc[row, 0]), int(b2down.columns[col])): int(b2down.iloc[row, col])
    for row in range(b2down.shape[0])
    for col in range(1, b2down.shape[1])
}

with open('static/data/B1UP_FARE_DICT.pickle', 'wb') as file:
    pickle.dump(b1up_dict_named, file)

with open('static/data/B1DOWN_FARE_DICT.pickle', 'wb') as file:
    pickle.dump(b1down_dict_named, file)
