import pandas as pd

df = pd.DataFrame(data=[1.5555555555e-01, 1, 1])
df.to_csv('data.csv', header=['params'])

df1 = pd.read_csv('data.csv', index_col=0)#'params')
d = df1.values
print(float(d[0, 0]))
print(float(d[1, 0]))
print(float(d[2, 0]))