file = open('relationships.csv','r')
next(file)
dict_pairs={}
counter_double=0
for line in file:
    splitted=line.split(',')
    if not (splitted[0],splitted[1]) in dict_pairs:
        dict_pairs[(splitted[0],splitted[1])]=1
    else:
        # print(line)
        counter_double+=1
        dict_pairs[(splitted[0],splitted[1])]+=1

print(counter_double)
for pair, counter in dict_pairs.items():
    if counter>1:
        print(pair,counter)
print(len(dict_pairs))