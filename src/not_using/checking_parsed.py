import pandas as pd

dat = pd.read_csv("parsed_logs.csv")
print(dat.tail())
print(dat.columns)
