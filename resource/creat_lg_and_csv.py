import re
import csv

rule1 = r'"id":(.*?),'
rule2 = r'"entity_type":(.*?),'

rule3 = r'"start_id":(.*?),'
rule4 = r'"target_id":(.*?),'
rule5 = r'"relationship_type":(.*?)}'

ary =[]
vertex = []
edge = []

with open('graph.json', 'r', encoding='utf-8')as f:
    for line in f:

        if "entity_type" in line:
            list1 = re.findall(rule1, line)
            list2 = re.findall(rule2, line)
            ary.append(list1[0])
            ary.append(list2[0])
            vertex.append(ary)
            ary = []
        if "relationship_type" in line:
            list1 = re.findall(rule3, line)
            list2 = re.findall(rule4, line)
            list3 = re.findall(rule5, line)
            ary.append(list1[0])
            ary.append(list2[0])
            ary.append(list3[0])
            edge.append(ary)
            ary = []

# print(vertex)
# print(edge)

outfile = open('graph.lg', 'w', encoding='utf-8')
outfile.write('#' + ' ' + 't' + ' ' + '1' + '\n')
for i in range(0, len(vertex)):
    outfile.write('v' + ' ' + vertex[i][0] + ' ' + vertex[i][1] + '\n')
for i in range(0, len(edge)):
    outfile.write('e' + ' ' + edge[i][0] + ' ' + edge[i][1] + ' ' + edge[i][2] + '\n')
outfile.close()

outfile = open('GraphVertices.csv', 'w', encoding='utf-8')
csv_writer = csv.writer(outfile)
for i in range(0, len(vertex)):
    csv_writer.writerow(vertex[i])
outfile.close()

outfile = open('GraphEdges.csv', 'w', encoding='utf-8')
csv_writer = csv.writer(outfile)
for i in range(0, len(edge)):
    csv_writer.writerow(edge[i])
outfile.close()