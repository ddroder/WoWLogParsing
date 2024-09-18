import pandas as pd

dat = pd.read_csv("test.csv")
print(dat)
print(dat.columns)
print(dat.loc[dat["spellName"].str.contains("Demonic Circle", na=False)])
dat_dc = dat.loc[dat["spellName"].str.contains("Nether", na=False)]
print(dat_dc[["spellName", "posX", "posY", "posZ"]])
