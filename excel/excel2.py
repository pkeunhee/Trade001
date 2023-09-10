import pandas as pd
from datetime import datetime
import numpy as np

# 수출입 총괄에서 월별 수입금액을 sum 하여 계절적 요인이 있는지 확인해보려고... 결론은 계절적 요인은 없는듯

df = pd.read_excel('/Users/ghp-m1/Downloads/수출입총괄_202309253.xls', skiprows=5,
                   names=['기간', '수출건수', '수출금액', '수입건수', '수입금액', '무역수지'],
                   dtype={'기간':str, '수출건수':str, '수출금액':str, '수입건수':str, '수입금액':str, '무역수지':str})


df['월'] = df['기간'].str.slice(5, 7)
df['기간'] = df['기간'].apply(lambda x: datetime.strptime(x, '%Y.%m').date())

df.set_index('기간', inplace=True)

cols = ['수출건수', '수출금액', '수입건수', '수입금액', '무역수지']
for col in cols:
    df[col] = (df[col].str.strip()).str.replace(',', '').astype(int)

df.groupby(['월'])['수입금액'].sum()

print('end')