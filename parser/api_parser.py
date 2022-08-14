import json
from unittest import result
from requests_html import HTMLSession

# example of url=https://api-moonriver.moonscan.io/
def parse(url, contract, topic, from_block, to_block):
    prev_last_last_block_number = -1
    result = []
    session = HTMLSession()
    while True:
        request = url + 'api?module=logs&action=getLogs&' + \
            'fromBlock=' + str(from_block) + '&toBlock=' + str(to_block) + \
            '&address=' + contract + '&topic0=' + topic
        response = session.get(request)
        events = json.loads(response.text)['result']
        if not events:
            break
        last_block_number = int(events[-1]['blockNumber'], 16)
        if last_block_number == prev_last_last_block_number:
            break
        prev_last_last_block_number = last_block_number
        from_block = last_block_number + 1
        result.extend(events)
    return result


        

