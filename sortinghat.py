import csv
import random
from random import shuffle

filename = 'form_responses.csv'
name_idx = -1
tele_handle_idx = -1

rows = []
with open(filename, 'r') as f:
    spamreader = csv.reader(f, delimiter=',')
    firstRow = None
    for row in spamreader:
        if(firstRow is None): 
            firstRow = row
            idx = 0
            for header in firstRow:
                h = header.lower()
                if(h == 'name'):
                    name_idx = idx
                elif('telegram handle' in h):
                    tele_handle_idx = idx
                idx += 1
        else:
            rows.append(row)
random.seed(42)
shuffle(rows)
print(rows)
for x in rows:
    x[tele_handle_idx] = x[tele_handle_idx].replace('@','')
idx = 0
with open(f'paired_{filename}', 'w') as f:
    writer = csv.writer(f)
    while(idx < len(rows)):
        writer.writerow([rows[idx][tele_handle_idx], rows[(idx+1)%len(rows)][tele_handle_idx]])
        idx+=1
