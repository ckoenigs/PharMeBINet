import numpy as np

g = open('blub.txt','r')

list_query=[]
list_filter=[]
length_file=5031
i=1
while i < length_file:
    next(g)
    query=next(g)
    list_query.append(float(query.split(' ')[0]))
    filter=next(g)
    list_filter.append(float(filter.split(' ')[0]))
    i+=3

print('query')
print(min(list_query))
print(max(list_query))
print(np.mean(list_query))

print('filter')
print(min(list_filter))
print(max(list_filter))
print(np.mean(list_filter))