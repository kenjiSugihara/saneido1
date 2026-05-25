import pandas as pd

# 1. データの読み込み
# ※文字化けする場合は encoding='shift_jis' または 'cp932' に変更してください
df = pd.read_csv('sales_data.csv', encoding='utf-8')

# 2. 日付型への変換と期間の絞り込み
df['売上日付'] = pd.to_datetime(df['売上日付'])
start_date = pd.to_datetime('2023-04-01') # 令和5年4月1日
end_date = pd.to_datetime('2026-04-30')   # 令和8年4月30日
df_filtered = df[(df['売上日付'] >= start_date) & (df['売上日付'] <= end_date)].copy()

# 3. 年度別の重みづけ関数
def get_weight(date):
    if pd.to_datetime('2025-04-01') <= date <= pd.to_datetime('2026-04-30'):
        return 6
    elif pd.to_datetime('2024-04-01') <= date <= pd.to_datetime('2025-03-31'):
        return 3
    elif pd.to_datetime('2023-04-01') <= date <= pd.to_datetime('2024-03-31'):
        return 1
    return 0

# 重みの適用と「重み付き売上高」の算出
df_filtered['重み'] = df_filtered['売上日付'].apply(get_weight)
df_filtered['重み付き売上高'] = df_filtered['税抜純売上高'] * df_filtered['重み']

# 4. 商品コード・商品名ごとの集計
grouped = df_filtered.groupby(['商品コード', '商品名'])['重み付き売上高'].sum().reset_index()

# 5. ABC分析のための並び替えと累計構成比の計算
# 売上高の降順にソート
grouped = grouped.sort_values(by='重み付き売上高', ascending=False).reset_index(drop=True)

# 構成比と累計構成比の計算
total_sales = grouped['重み付き売上高'].sum()
grouped['売上構成比'] = grouped['重み付き売上高'] / total_sales
grouped['累計売上構成比'] = grouped['売上構成比'].cumsum()

# 6. ABCランクの割り当て (A: 上位20%, B: 次の60%, C: 下層20%)
def assign_abc(cumulative_ratio):
    if cumulative_ratio <= 0.20:
        return 'A'
    elif cumulative_ratio <= 0.80:
        return 'B'
    else:
        return 'C'

grouped['ABCランク'] = grouped['累計売上構成比'].apply(assign_abc)

# 7. 結果を新しいCSVとして保存
grouped.to_csv('三英堂_ABC分析結果.csv', index=False, encoding='utf-8-sig')
print("分析が完了し、「三英堂_ABC分析結果.csv」が作成されました。")
print(grouped.head(10)) # 上位10件を表示
