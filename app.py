import streamlit as st
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from pyarrow.jvm import record_batch

# 讓 matplotlib 能顯示中文（Mac / Windows / 雲端都試試看）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang TC', 'Microsoft JhengHei', 'Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

FILE = 'records.json'



def load_records():
    if not os.path.exists(FILE):
        return []
    with open(FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_records(records):
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

if st.button('清空'):
    os.remove("records.json")

st.title('💰 我的零用錢記帳本')

records = load_records()

with st.form('add_form', clear_on_submit=True):
    date = st.date_input('日期')
    kind = st.radio('收入還是支出？', ['支出', '收入'], horizontal=True)
    category = st.selectbox('類別', ['飲食', '交通', '娛樂', '文具', '零用錢', '其他'])
    item = st.text_input('項目', placeholder='例如：珍奶')
    amount = st.number_input('金額', min_value=0, step=10)
    submitted = st.form_submit_button('記下來')

if submitted:
    if item == '' or amount == 0:
        st.error('項目和金額都要填喔！')
    else:
        records.append({'日期': str(date), '收支': kind, '類別': category,
                        '項目': item, '金額': amount})
        save_records(records)
        st.success(f'已記下：{item} {amount} 元')

income = 0
expense = 0
for r in records:
    if r['收支'] == '收入':
        income += r['金額']
    else:
        expense += r['金額']

col1, col2, col3 = st.columns(3)
col1.metric('總收入', f'{income} 元')
col2.metric('總支出', f'{expense} 元')
col3.metric('餘額', f'{income - expense} 元')

st.subheader('明細')
st.dataframe(records)

# ---- 圖一：各類別支出圓餅圖 ----
st.subheader('錢都花到哪裡去了？')
totals = {}   # 例如 {'飲食': 300, '交通': 120}
for r in records:
    if r['收支'] == '支出':
        totals[r['類別']] = totals.get(r['類別'], 0) + r['金額']

if totals:
    fig, ax = plt.subplots()
    ax.pie(list(totals.values()), labels=list(totals.keys()), autopct='%1.0f%%')
    st.pyplot(fig)
else:
    st.info('還沒有支出記錄')

# ---- 圖二：餘額變化折線圖（用 numpy 累加）----
st.subheader('餘額變化')
if records:
    records_sorted = sorted(records, key=lambda r: r['日期'])   # 依日期排序
    changes = []
    for r in records_sorted:
        if r['收支'] == '收入':
            changes.append(r['金額'])
        else:
            changes.append(-r['金額'])
    balance = np.cumsum(changes)   # 一路累加：[100, 45, 25, ...]

    fig, ax = plt.subplots()
    ax.plot(range(1, len(balance) + 1), balance, marker='o')
    ax.axhline(0, color='red', linewidth=1)   # 0 元的紅線，低於它就是透支
    ax.set_xlabel('第幾筆')
    ax.set_ylabel('餘額（元）')
    st.pyplot(fig)
