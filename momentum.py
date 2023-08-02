import pandas as pd

df = pd.read_excel("data/merge.xlsx")
df['일자'] = pd.to_datetime(df['일자'], format="%Y%m%d")
df = df.set_index('일자')
return_df = df.pct_change(60)
s = return_df.loc["2023-01-17"]
momentum_df = pd.DataFrame(s)
momentum_df.columns = ["모멘텀"]
momentum_df.head(n=10)
momentum_df['순위'] = momentum_df['모멘텀'].rank(ascending=False)
momentum_df.head(n=10)
momentum_df = momentum_df.sort_values(by='순위')
momentum_df[:30]

print(momentum_df)