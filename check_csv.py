import pandas as pd
df = pd.read_csv('https://raw.githubusercontent.com/PyThaiNLP/thai-synonym/master/data.csv')
print(df.head(10))
print(df.columns.tolist())
print(f"จำนวนแถว: {len(df)}")