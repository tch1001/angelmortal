import csv

form_filename = 'form_responses.csv'
pairs_filename = f'paired_{form_filename}'
pairs = {}
with open(pairs_filename, 'r') as f:
    spamreader = csv.reader(f, delimiter=',')
    for row in spamreader:
        if(row[0] in pairs):
            print(f"{row[0]} seems to have more than one mortal??")
            exit()
        pairs[row[0]] = row[1]

visited = {}
stats = []
for x in pairs.keys():
    if(x in visited):
        continue
    visited[x] = True
    loop_size = 1
    loop = [x]
    cur = pairs[x]
    while(cur != x):
        if(cur in visited):
            print(f'i think you should double check that {cur} does not have more than 1 angel')
            break
        loop_size += 1
        loop.append(cur)
        visited[cur] = True
        cur = pairs[cur]
    stats.append((loop_size, loop))
for x in sorted(stats, reverse=True):
    print(x[0], ','.join(x[1]))