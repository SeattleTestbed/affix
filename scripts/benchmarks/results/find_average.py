import sys

fileobj = open(sys.argv[1])
filecontent = fileobj.read()

overall_dict = {}

for curline in filecontent.split('\n'):
    if not curline:
        continue

    category, junk, data = curline.split(':')

    if category not in overall_dict.keys():
        overall_dict[category] = []

    # Get rid of the KB/s from the string.
    throughput = float(data.split()[0])
    overall_dict[category].append(throughput)



for curkey in overall_dict.keys():
    totalput = 0

    for curthroughput in overall_dict[curkey]:
        totalput += curthroughput

    print curkey +': ' + str(totalput/len(overall_dict[curkey]))
