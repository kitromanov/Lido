import json
import pandas

# 18 February
ksm_start_timestamp = 1645162428

def cut(start_timestamp, file):
    ptr = 0
    for row in file:
        if row[0] <= start_timestamp:
            return file[ptr:]
        ptr += 1
    return file

with open('excel_data/deposit_count.json', 'r') as deposit_count, \
    open('excel_data/redeem_count.json', 'r') as redeem_count, \
    open('excel_data/total_rewards.json', 'r') as total_rewards, \
    open('excel_data/total_holders.json', 'r') as total_holders, \
    open('excel_data/total_staked.json', 'r') as total_staked, \
    open('excel_data/apr.json') as apr:
    deposit_count_excel = pandas.DataFrame(cut(ksm_start_timestamp, json.load(deposit_count)))
    redeem_count_excel = pandas.DataFrame(json.load(redeem_count))
    total_rewards_excel = pandas.DataFrame(json.load(total_rewards))
    total_holders_excel = pandas.DataFrame(json.load(total_holders))
    total_staked_excel = pandas.DataFrame(json.load(total_staked))
    apr_excel = pandas.DataFrame(json.load(apr))
    writer = pandas.ExcelWriter('Kusama lido metrics.xlsx', engine='xlsxwriter')
    deposit_count_excel.to_excel(writer, sheet_name = 'Deposits count', index=False, header=False)
    redeem_count_excel.to_excel(writer, sheet_name = 'Redeems count', index=False, header=False)
    total_rewards_excel.to_excel(writer, sheet_name = 'Total rewards', index=False, header=False)
    total_holders_excel.to_excel(writer, sheet_name = 'Holders', index=False, header=False)
    total_staked_excel.to_excel(writer, sheet_name = 'Total staked', index=False, header=False)
    apr_excel.to_excel(writer, sheet_name = 'APR', index=False, header=False)
    writer.save()
