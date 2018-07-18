import csv, datetime, sys
import matplotlib.pylab as plt

print (datetime.datetime.utcnow())
if len(sys.argv)>2:
    read_file=sys.argv[1]
    write_file=sys.argv[2]
else:
    print('need a read file with inference score and a write file')
    sys.exit()
file = open(read_file,'r')
other_file= open(write_file,'w')
dict_scores={}
csv_reader= csv.DictReader(file)
counter=0
for line in csv_reader:
    counter += 1
    score=line['InferenceScore']
    if score!='':
        score=float(score)
        if score in dict_scores:
            dict_scores[score]+=1
        else:
            dict_scores[score]=1
    if counter%1000000==0:
        print(counter)
        print (datetime.datetime.utcnow())

print (datetime.datetime.utcnow())
print(len(dict_scores))

list_of_keys= dict_scores.keys()
list_of_keys.sort(reverse=True)
summe=0
number_of_scores=0
for key in list_of_keys:
    other_file.write(str(key)+':'+str(dict_scores[key])+'\n')
    summe+= (key*dict_scores[key])
    number_of_scores+= dict_scores[key]

print (datetime.datetime.utcnow())
mean=summe/number_of_scores
print(mean)
lists=sorted(dict_scores.items())
x,y= zip(*lists)
plt.plot(x,y)
plt.show()