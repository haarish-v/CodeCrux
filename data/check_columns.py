import pandas as pd
import glob

files = glob.glob("C:/Codecrux/data/bidmc/bidmc_csv/*.csv")

for f in files:
    print("\n----", f)
    df = pd.read_csv(f)
    print(df.columns.tolist())