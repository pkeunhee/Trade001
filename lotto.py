import pandas as pd

df = pd.read_excel("data/lotto_his.xlsx")
df.columns = ['seq', 'date', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'b']
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
df = df.set_index('date')

# freq = df.groupby(['n1', 'n2', 'n3', 'n4', 'n5', 'n6']).size()
# freq = df.groupby(['n3']).size()
freq = df.value_counts(['n1', 'n2', 'n3', 'n4', 'n5', 'n6']).max()
print(freq)

