import json

ratiolist = []
file = open('ratios.dat')

for line in file:
    ratiolist.append(json.loads(line))

file.close()


maxlength = max([len(list) for list in ratiolist])


datalist = []
for i in range(maxlength):
    numberlist = []
    for list in ratiolist:
        numberlist += list[i:i+1]
    datalist.append(numberlist)


outfile = open('data.json', 'w')

json.dump(datalist, outfile)

outfile.close()
