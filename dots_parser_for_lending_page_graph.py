import pylightxl as xl
from parse_settings import network, path_to_work_book, apr_week_column, key_column, nominated_stake_column, ranges, result_file
from statistics import mean
import operator
import os

def add_value_to_validator(validators, key, value):
    if validators.get(key) == None:
        validators[key] = [value]
    else:
        validators[key].append(value)

work_book = xl.readxl(fn=path_to_work_book)
if network == 'kusama':
    eras = work_book.ws_names[-28:]
elif network == 'polkadot':
    eras = work_book.ws_names[-7:]
validators_apr_week = {}
validators_nominated_stake = {}
for era in eras:
    for row in work_book.ws(ws=era).rows:
        key = row[key_column]
        apr_week = row[apr_week_column] if not isinstance(row[apr_week_column], str) else 0
        #nominated stake field is missing, go to the next era
        if len(row) < nominated_stake_column:
            break
        nominated_stake = row[nominated_stake_column] if not isinstance(row[nominated_stake_column], str) else 0
        if apr_week:
            add_value_to_validator(validators_apr_week, key, apr_week)
            add_value_to_validator(validators_nominated_stake, key, nominated_stake)
validators_apr_staked = []
for validator in validators_apr_week:
    avg_apr = mean(validators_apr_week[validator]) 
    avg_staked = mean(validators_nominated_stake[validator])
    validators_apr_staked.append([validator, avg_apr, avg_staked])
sorted_by_apr_validators = sorted(validators_apr_staked, key=operator.itemgetter(1))
ranges_count = len(ranges)
validators_by_intervals = {x: {'apr_week': [], 'nominated_stake': []} for x in range(ranges_count)}
current_interval = 0
itr = 0
for validator in sorted_by_apr_validators:
    while current_interval < ranges_count and ranges[current_interval][1] < validator[1]:
        current_interval += 1
    if current_interval >= ranges_count:
        break
    validators_by_intervals[current_interval]['apr_week'].append(validator[1])
    validators_by_intervals[current_interval]['nominated_stake'].append(validator[2])
    itr+=1
dots = []
for interval in range(ranges_count):
    x = mean(validators_by_intervals[interval]['apr_week'])    
    y = mean(validators_by_intervals[interval]['nominated_stake'])
    dots.append([x, y])

if not os.path.exists(os.path.dirname('out/')):
    dir_name = os.path.dirname('out/')
    os.makedirs(dir_name)
with open('out/' + result_file, 'w') as f:
    for i in range(ranges_count):
        f.write(f'{i+1}: {dots[i][0]}, {dots[i][1]}\n')

    
