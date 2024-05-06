import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from io import StringIO
import os

browser = webdriver.Chrome()
url = 'https://finance.naver.com/sise/sise_market_sum.naver?&page='
browser.get(url)

checkboxes = browser.find_elements(By.NAME, 'fieldIds')
for checkbox in checkboxes:
    if checkbox.is_selected():
        checkbox.click()

items_to_select = ['시가총액', 'PER', 'ROA']
for checkbox in checkboxes:
    parent = checkbox.find_element(By.XPATH, '..')
    label = parent.find_element(By.TAG_NAME, 'label')
    # print(label.text)
    if label.text in items_to_select:
        checkbox.click()

btn_apply = browser.find_element(By.XPATH, '//a[@href="javascript:fieldSubmit()"]')
btn_apply.click()

f_name = 'sise.csv'
df_list = []
for idx in range(1, 3):
    browser.get(url + str(idx))
    df = pd.read_html(StringIO(browser.page_source))[1]
    df.dropna(axis='index', how='all', inplace=True)
    df.dropna(axis='columns', how='all', inplace=True)
    if len(df) == 0:
        break
    df_list.append(df)


merged_df = pd.concat(df_list, ignore_index=True)


filtered_df = merged_df[(merged_df['PER'] >= 10)]
per_mean = filtered_df['PER'].mean()
roa_mean = filtered_df['ROA'].mean()

filtered_df['per_score'] = 100 - ((filtered_df['PER'] - per_mean) / per_mean) * 50
filtered_df['roa_score'] = ((filtered_df['ROA'] - roa_mean) / roa_mean) * 50 + 50
filtered_df['total_score'] = filtered_df['per_score'] + filtered_df['roa_score']
filtered_df = filtered_df.sort_values(by='total_score', ascending=False)

filtered_df.to_csv(f_name, encoding='utf-8-sig', index=False)

browser.quit()

