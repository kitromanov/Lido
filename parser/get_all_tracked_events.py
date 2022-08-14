# Сollecting all the events via api
from api_parser import parse
import json
import os

from_block = 1462819 
# from_block = 800000 #906643
to_block = 2379600
# to_block = 1650427 #1645577
moonriver_url='https://api-moonriver.moonscan.io/'
# moonbeam_url='https://api-moonbeam.moonscan.io/'
ksm_lido = '0xFfc7780C34B450d917d557E728f033033CB4fA8C'
# polkadot_lido = '0xFA36Fe1dA08C89eC72Ea1F0143a35bFd5DAea108'
tracked_events = ['deposit', 'redeem', 'rewards', 'transfer']
event_topic0 = {'deposit' : '0x2da466a7b24304f47e87fa2e1e5a81b9831ce54fec19055ce277ca2f39ba42c4',
'redeem' : '0x4896181ff8f4543cc00db9fe9b6fb7e6f032b7eb772c72ab1ec1b4d2e03b9369', 
'rewards' : '0x61953b03ced70bb23c53b5a7058e431e3db88cf84a72660faea0849b785c43bd',
'transfer' : '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'}


if __name__ == "__main__":
    if not os.path.exists(os.path.dirname('events/')):
        dir_name = os.path.dirname('events/')
        os.makedirs(dir_name)
    for event in tracked_events:
        result = parse(moonriver_url, ksm_lido, event_topic0[event], from_block, to_block)
        with open('events/' + event + '_events.json', 'w') as output:
            json.dump(result, output)