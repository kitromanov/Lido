#Process events for excel by 6 metrics
import json
import web3
import datetime
from operator import itemgetter

base = 10**12
# base = 10**10
size_data_block = 64
ksm_lido = '0xFfc7780C34B450d917d557E728f033033CB4fA8C'
# polkadot_lido = '0xFA36Fe1dA08C89eC72Ea1F0143a35bFd5DAea108'
rpc_url='https://moonriver.blastapi.io/ef63a3d6-da02-4f53-b6f1-ed5ed03fc2fa'
# rpc_url='https://moonbeam.public.blastapi.io'
storage_total_supply_index = 5
event_topic0 = {'deposit' : '0x2da466a7b24304f47e87fa2e1e5a81b9831ce54fec19055ce277ca2f39ba42c4',
'redeem' : '0x4896181ff8f4543cc00db9fe9b6fb7e6f032b7eb772c72ab1ec1b4d2e03b9369', 
'rewards' : '0x61953b03ced70bb23c53b5a7058e431e3db88cf84a72660faea0849b785c43bd',
'transfer' : '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'}
zero = '0x0000000000000000000000000000000000000000000000000000000000000000'

def get_deposit_redeem_count(event_file, excel_file):
    result = []
    with open(event_file) as input:
        events = json.load(input)
    cntr = 0
    for event in events:
        timestamp = int(event['timeStamp'], 16)
        cntr += 1
        result.append([timestamp, cntr])
    with open(excel_file, 'w') as output:
        json.dump(result, output)

def get_total_rewards(event_file, excel_file):
    result = []
    with open(event_file) as input:
        events = json.load(input)
    total = 0
    for event in events:
        timestamp = int(event['timeStamp'], 16)
        total += (int(event['data'][2:][size_data_block:size_data_block*2], 16) / base)
        result.append([timestamp, total])
    with open(excel_file, 'w') as output:
        json.dump(result, output)

def merge_json_files(files, path):
    result = list()
    for file in files:
        with open(path + file, 'r') as input:
            data = json.load(input)
            result.extend(data)
    return result

# Run through all the events: deposit, redeem,
# reward, transfer in time-sorted order and
# look at total_supply in storage
def get_total_staked(contract, excel_file):
    result = []
    event_files = ['deposit_events.json', 'redeem_events.json', 'rewards_events.json', 'transfer_events.json']
    all_events = merge_json_files(event_files, 'events/')
    with open('events/all_events.json', 'w') as output:
        json.dump(all_events, output)
    blocks = set()
    timestamp_to_block = {}
    for event in all_events:
        timestamp = int(event['timeStamp'], 16)
        block_number = int(event['blockNumber'], 16)
        timestamp_to_block[block_number] = timestamp
        blocks.add(block_number)
    sorted_blocks = sorted(list(blocks))
    w3 = web3.Web3(web3.HTTPProvider(rpc_url))
    cntr = 0
    print(datetime.datetime.now(), 'block amount', len(sorted_blocks))
    for block in sorted_blocks:
        cntr += 1
        total_supply_to_block = w3.toInt(w3.eth.getStorageAt(contract, storage_total_supply_index, block)) / base
        result.append([timestamp_to_block[block], total_supply_to_block])
        if cntr % 1000 == 0:
            print('alive', total_supply_to_block, datetime.datetime.now())
    print(datetime.datetime.now())
    with open(excel_file, 'w') as output:
        json.dump(result, output)

# Apr is calculated as the average for the last 100 eras
def get_apr(event_file, excel_file):
    result = []
    with open(event_file) as input:
        events = json.load(input)
    array_size = 100
    ptr = 0
    last_apr = [0] * array_size
    sum = 0
    iteration_cntr = 0
    for event in events:
        iteration_cntr += 1
        timestamp = int(event['timeStamp'], 16)
        reward = int(event['data'][2:][size_data_block:size_data_block*2], 16)
        ledger_balance = int(event['data'][2:][size_data_block * 2:size_data_block*3], 16)
        current_apr = 4*365 * ledger_balance / (ledger_balance - reward)
        sum += current_apr
        if iteration_cntr <= 100:
            last_apr[ptr] = current_apr
            result.append([timestamp, (sum / iteration_cntr) / 100])
        else:
            sum -= last_apr[ptr % array_size]
            last_apr[ptr % array_size] = current_apr
            print(iteration_cntr, sum, iteration_cntr, (sum / 100) * 0.01)
            result.append([timestamp, (sum / array_size) / 100])
        ptr += 1
    with open(excel_file, 'w') as output:
        json.dump(result, output)

def get_total_holders(excel_file):
    result = []
    event_files = ['deposit_events.json', 'redeem_events.json', 'transfer_events.json']
    deposit_redeem_transfer = merge_json_files(event_files, 'events/')
    with open('events/merged_deposit_redeem_transfer.json', 'w') as output:
        json.dump(deposit_redeem_transfer, output)
    sorted_events = sorted(deposit_redeem_transfer, key=itemgetter('timeStamp'))
    balances = {}
    total_holders = 0
    for event in sorted_events:
        timestamp = int(event['timeStamp'], 16)
        account = event['topics'][1]
        amount = int(event['data'], 16)
        if event['topics'][0] == event_topic0['deposit']:
            if balances.get(account) == None:
                balances[account] = [amount, timestamp]
                total_holders += 1
            else:
                balances[account] = [amount + balances[account][0], timestamp]
        elif event['topics'][0] == event_topic0['redeem']:
            if balances.get(account) == None or balances[account][0] < amount:
                continue
            balances[account] = [balances[account][0] - amount, timestamp]
            if balances[account][0] <= 0:
                total_holders -= 1
        else:
            account_to = event['topics'][2]
            if balances.get(account) == None or balances[account][0] < amount:
                continue
            # in the redeem function there are two events transfer and redeem
            # checking for double subtraction
            # if balances[account][1] != timestamp:
            #     balances[account] = [balances[account][0] - amount, timestamp]
            # if balances[account][0] <= 0:
            #     total_holders -= 1
            if balances.get(account_to) == None:
                balances[account_to] = [amount, timestamp]
                total_holders += 1
            else:
                balances[account_to] = [amount + balances[account_to][0], timestamp]
            result.append([timestamp, total_holders])
    with open(excel_file, 'w') as output:
        json.dump(result, output)

# def get_total_holders(excel_file):
#     result = []
#     event_files = ['deposit_events.json', 'redeem_events.json', 'transfer_events.json']
#     deposit_redeem_transfer = merge_json_files(event_files, 'events/')
#     with open('events/merged_deposit_redeem_transfer.json', 'w') as output:
#         json.dump(deposit_redeem_transfer, output)
#     sorted_events = sorted(deposit_redeem_transfer, key=itemgetter('timeStamp'))
#     balances = {}
#     total_holders = 0
#     for event in sorted_events:
#         timestamp = int(event['timeStamp'], 16)
#         account = event['topics'][1]
#         amount = int(event['data'], 16)
#         if amount == 0:
#             continue
#         if event['topics'][0] == event_topic0['transfer']:
#             account_to = event['topics'][2]
#             if account == zero:
#                 if balances.get(account_to) == None:
#                     balances[account_to] = amount
#                     total_holders += 1
#                 else:
#                     if balances[account_to] <= 0 and balances[account_to] + amount > 0:
#                         total_holders += 1
#                     balances[account_to] += amount
#             elif account_to == zero:
#                 balances[account] -= amount
#                 if balances[account] <= 0:
#                     total_holders -= 1
#             # stake to curve pool
#             # elif account_to == '0x0000000000000000000000000ffc46cd9716a96d8d89e1965774a70dcb851e50':
#             #     if balances.get(account_to) == None:
#             #         balances[account_to] = amount
#             #         total_holders += 1
#             #     else:
#             #         if balances[account_to] <= 0 and balances[account_to] + amount > 0:
#             #             total_holders += 1
#             #         balances[account_to] += amount
#             else:
#                 balances[account] -= amount
#                 if balances[account] <= 0:
#                     total_holders -= 1
#                 if balances.get(account_to) == None:
#                     balances[account_to] = amount
#                     total_holders += 1
#                 else:
#                     if balances[account_to] <= 0 and balances[account_to] + amount > 0:
#                         total_holders += 1
#                     balances[account_to] += amount
#             result.append([timestamp, total_holders])
#     with open(excel_file, 'w') as output:
#         json.dump(result, output)


if __name__ == "__main__":
    # get_deposit_redeem_count('events/redeem_events.json', 'excel_data/redeem_count.json')
    # get_total_rewards('events/rewards_events.json', 'excel_data/total_rewards.json')
    get_total_staked(ksm_lido, 'excel_data/total_staked.json')
    # get_apr('events/rewards_events.json', 'excel_data/apr.json')
    # get_total_holders('excel_data/total_holders.json')
