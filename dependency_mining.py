from itertools import combinations  
import pandas as pd
import numpy as np
import operator
import time
import copy
import sys

'''
the final version
'''

#generate dependencies based on the link between above layer and below layer
class Literal:
    '''
    the strcture of one literal
    '''
    attributeLabel = -1 
    def __init__(self,identity,variable,attribute,value,isEqual,eqVari,eqAttri,equalClass,entityType):
        self.identity = identity
        self.variable = variable
        self.attribute = attribute
        self.value = value
        self.isEqual = isEqual
        self.eqVari = eqVari
        self.eqAttri = eqAttri
        self.equalClass = equalClass
        self.entityType = entityType

    def getValue(self):
        if self.isEqual:
            return "%s.%s=%s.%s" % (self.eqVari[0],self.eqAttri[0],self.eqVari[1],self.eqAttri[1])
        else:
            return "%s.%s=%s" % (self.variable,self.attribute,self.value)

    def __repr__(self):
        if self.isEqual:
            return "%s.%s=%s.%s" % (self.eqVari[0],self.eqAttri[0],self.eqVari[1],self.eqAttri[1])
        else:
            return "%s.%s=%s" % (self.variable,self.attribute,self.value)

class Block:
    '''
    the strcture of one block of each lattice level
    '''
    def __init__(self,attributeLabels,literalsSet):
        self.attributeLabels = attributeLabels
        self.literalsSet = literalsSet
    def __repr__(self):
        return str(self.attributeLabels)

'''
param: attribute: the values of a variable attribute in dataTable
return: the partition of the values of a variable attribute
'''
def create_Attribute_Paritition(attrValues):
    tmpl = attrValues.to_dict()
    ini_dict = tmpl
    flipped = {}
    for key, value in ini_dict.items():
        if value not in flipped.keys():
            flipped[value] = [key]
        else:
            flipped[value].append(key)
    return flipped

'''
return: the set of all literals in dataTable, the number of attributes
'''
def generLiterals(readFile,attriNumberLimit):
    filename = readFile
    df = pd.read_csv(filename,delimiter=";;",engine='python')
    # constrain the number of attributes
    if attriNumberLimit != -1:
        df = df.iloc[0:len(df.index),0:attriNumberLimit]

    literals = []
    temp1 = 0
    # execute literal situation a
    for colName  in df.columns:
        partiton = create_Attribute_Paritition(df[colName])
        #print(partiton)
        variable = colName.split(".")[0].split(":")[1].split(")")[0]
        attribute = colName.split(".")[1]
        entityType = colName.split(".")[0].split(":")[0].split("(")[1]
        if attribute!="id":
            for value in partiton.keys():
                # value is not null
                if value==value and value!="N":
                    equalClass = tuple(partiton[value])
                    literals.append(Literal(temp1,variable,attribute,value,False,None,None,equalClass,entityType))
                    temp1 += 1
    # print(literals)
    # execute literal situation b&c
    # situationBdic: {1: {y0:[name,id,genre],y1:[id,name,genre,year]}}
    situationBdic = {}
    for colName in df.columns:
        variable = colName.split(".")[0].split(":")[1].split(")")[0]
        attribute = colName.split(".")[1]
        entityType = colName.split(".")[0].split(":")[0].split("(")[1]
        if entityType not in situationBdic.keys():
            situationBdic[entityType] = {}
        if variable in situationBdic[entityType].keys():
            situationBdic[entityType][variable].append(attribute)
        else:
            situationBdic[entityType][variable] = [attribute]
    situations = []
    for entityType in situationBdic.keys():
        for ent1Name, ent2Name in combinations(situationBdic[entityType].keys(),2):
            ent1Attris = situationBdic[entityType][ent1Name]
            ent2Attris = situationBdic[entityType][ent2Name]
            for attriName in ent1Attris:
                if attriName in ent2Attris:
                    literalB = ent1Name+"."+attriName+"="+ent2Name+"."+attriName
                    situations.append([entityType,literalB])
    #print(situations)
    for situation in situations:
        entityType = situation[0]
        vari1 = situation[1].split("=")[0].split(".")[0]
        attri1 = situation[1].split("=")[0].split(".")[1]
        vari2 = situation[1].split("=")[1].split(".")[0]
        attri2 = situation[1].split("=")[1].split(".")[1]
        se = pd.Series(df["("+entityType+":"+vari1+")"+"."+attri1]==df["("+entityType+":"+vari2+")"+"."+attri2])
        equalClass = tuple(se[se].index)
        literals.append(Literal(temp1,"None",attri1,None,True,(vari1,vari2),(attri1,attri2),equalClass,entityType))
        temp1 += 1
    # generate the attributeLabel for each literal
    attriLabelSet = set()
    for literal in literals:
        attriLabel = str(literal.entityType)+"."+literal.attribute
        attriLabelSet.add(attriLabel)
    attriLabelSet = list(attriLabelSet)
    attriLabelSet.sort()
    print(attriLabelSet)
    dicting1 = {}
    attributeLabel = 0
    for attriLabel in attriLabelSet:
        dicting1[attriLabel] = attributeLabel
        attributeLabel+=1
    for literal in literals:
        literal.attributeLabel = dicting1[str(literal.entityType)+"."+literal.attribute]
    return literals,len(attriLabelSet)

'''
output: the dependencies of one level
'''
def compute_dependencies_and_prune(levelSet1,levelSet2,dependency_set):
    for block1 in levelSet1:
        attributeLabels_1 = block1.attributeLabels
        for block2 in levelSet2:
            attributeLabels_2 = block2.attributeLabels
            if (set(attributeLabels_1).issubset(set(attributeLabels_2))):
                rhsIndex = -1000
                for i in range(len(attributeLabels_2)):
                    if attributeLabels_2[i] not in attributeLabels_1:
                        rhsIndex = i
                        break
                # print(attributeLabels_1,attributeLabels_2,rhsIndex)
                prefixHashMap = dict()
                reLiteralsSet = []
                for literals2 in block2.literalsSet:
                    keyStr = ''
                    for k in range(len(literals2)):
                        if k != rhsIndex:
                            keyStr += str(literals2[k].identity)
                    if (keyStr in prefixHashMap.keys()):
                        prefixHashMap[keyStr].append([literals2, literals2[rhsIndex]])
                    else:
                        prefixHashMap[keyStr] = [[literals2, literals2[rhsIndex]]]
                for literals1 in block1.literalsSet:
                    lhsSet = literals1
                    lhsMatches = lhsSet[0].equalClass
                    for literal in lhsSet:
                        lhsMatches = tuple(set(lhsMatches).intersection(set(literal.equalClass)))
                    keyStr = ''
                    for k in range(len(literals1)):
                        keyStr += str(literals1[k].identity)
                    if (keyStr in prefixHashMap.keys()):
                        for value in prefixHashMap[keyStr]:
                            rhs = value[1]
                            rhsMatches = rhs.equalClass
                            if (set(lhsMatches).issubset(set(rhsMatches))):
                                # isUseful = False
                                # tmp = rhs.variable
                                # for literal in lhsSet:
                                #     if tmp!=literal.variable or tmp=="None" or literal.variable=="None":
                                #         # more than one entity in dependency
                                #         isUseful = True
                                #         break
                                # if isUseful:
                                dependency = ""
                                for i in range(len(lhsSet)):
                                    if (i==len(lhsSet)-1):
                                        dependency += lhsSet[i].getValue()
                                    else:
                                        dependency += lhsSet[i].getValue()+";;"        
                                dependency += "->"
                                dependency += rhs.getValue()
                                # print(dependency)
                                dependency_set.append(dependency)
                                reLiteralsSet.append(value[0])
                for reliterals in reLiteralsSet:
                    # prune
                    block2.literalsSet.remove(reliterals)

'''
main method
'''
def mainMethod(readFile,dependency_set,information,attriNumberLimit):
    literals,attriNumber = generLiterals(readFile,attriNumberLimit)
    information.append("literalNumber "+str(len(literals))+" attriNumber "+str(attriNumber))
    # the initialization of lattice
    level = 0
    lattice = []
    level0Set = []
    L = []
    for i in range(attriNumber):
        L.append((i,))
    for attriLabels in L:
        # print(attriLabels[0])
        literalsSet = []
        for literal in literals:
            if literal.attributeLabel==attriLabels[0]:
                literalsSet.append([literal])
                # print(literal)
        level0Set.append(Block([attriLabels[0]],literalsSet))
    lattice.append(level0Set)
    # lattice generation
    for i in range(1,attriNumber):
        levelSet = []
        print("level ",i)
        start_time = time.time()
        for block1Index, block2Index in combinations([j for j in range(len(lattice[i-1]))], 2):
            block1 = lattice[i-1][block1Index]
            block2 = lattice[i-1][block2Index]
            prefixSame = True
            if (len(block1.attributeLabels)>1):
                # only the set which the prefixs are same can be combined to generate a new set in the next level
                if (not(operator.eq(block1.attributeLabels[0:len(block1.attributeLabels)-1],block2.attributeLabels[0:len(block2.attributeLabels)-1]))):
                    prefixSame = False
            if (len(block1.literalsSet)!=0 and len(block2.literalsSet)!=0 and prefixSame):
                literalsSet = []
                attributeLabels = []
                combineFirstOrder = 1
                if block1.attributeLabels[len(block1.attributeLabels)-1] < block2.attributeLabels[len(block2.attributeLabels)-1]:
                    attributeLabels = copy.deepcopy(block1.attributeLabels)
                    attributeLabels.append(block2.attributeLabels[len(block2.attributeLabels)-1])
                else:
                    combineFirstOrder = 2
                    attributeLabels = copy.deepcopy(block2.attributeLabels)
                    attributeLabels.append(block1.attributeLabels[len(block1.attributeLabels)-1])
                prefixHashMap = dict()          
                for literals1 in block1.literalsSet:
                    keyStr = ''
                    for k in range(len(literals1)-1):
                        keyStr += str(literals1[k].identity)
                    if (keyStr in prefixHashMap.keys()):
                        prefixHashMap[keyStr].append(literals1[len(literals1)-1])
                    else:
                        prefixHashMap[keyStr] = [literals1[len(literals1)-1]]
                for literals2 in block2.literalsSet:
                    keyStr = ''
                    for k in range(len(literals2)-1):
                        keyStr += str(literals2[k].identity)
                    if (keyStr in prefixHashMap.keys()):
                        if (combineFirstOrder==1):
                            for literal in prefixHashMap[keyStr]:
                                literalSet = literals2[0:len(literals2)-1]
                                literalSet.append(literal)
                                literalSet.append(literals2[len(literals2)-1])
                                matches = literalSet[0].equalClass
                                for literal in literalSet:
                                    matches = tuple(set(matches).intersection(set(literal.equalClass)))
                                if len(matches)>0:
                                    literalsSet.append(literalSet)
                        else:
                            for literal in prefixHashMap[keyStr]:
                                literalSet = copy.deepcopy(literals2)
                                literalSet.append(literal)
                                matches = literalSet[0].equalClass
                                for literal in literalSet:
                                    matches = tuple(set(matches).intersection(set(literal.equalClass)))
                                if len(matches)>0:
                                    literalsSet.append(literalSet)  
                if (len(literalsSet)>0):
                    levelSet.append(Block(attributeLabels,literalsSet))
                    print("one_block_literals_number",len(literalsSet))
        level += 1
        print("levelSet",len(levelSet))
        end_time = time.time()
        print('one_level_combination_time_cost',end_time - start_time, "s")
        start_time = time.time()
        lattice.append(levelSet)
        compute_dependencies_and_prune(lattice[i-1],lattice[i],dependency_set)
        end_time = time.time()
        print('one_level_compute_dependencies_time_cost',end_time - start_time, "s")
        lattice[i-1] = []
    print("literals number",len(literals))
    print("attribute number",attriNumber)

def clean_redundant(dependency_set,fileout,information):
    # for dependency in dependency_set:
    #     print(dependency)
    res_dict = {}
    rel_dict = {}
    for dependency in dependency_set:
        s = dependency.split('->')
        s1 = s[0]
        s2 = s[-1]
        if s1 in rel_dict.keys():
            tem = rel_dict[s1]
            tem.append(s2)
            rel_dict[s1] = tem.copy()
            res_dict[s1] = tem.copy()
        else:
            lists = [s2]
            rel_dict[s1] = lists.copy()
            res_dict[s1] = lists.copy()
    
    vaildNumber = 0
    for item in rel_dict.items():
        key = item[0]
        value = item[1]
        sli = key.split(';;')
        validSet = value.copy()
        for single_value in value:
            if len(sli) == 2:
                # A,B->C, A,C->B
                for i in range(0, 2):
                    new_str1 = sli[i] + ';;' + single_value
                    new_str2 = single_value + ';;' + sli[i]
                    new_value1 = []
                    new_value2 = []
                    if new_str1 in res_dict.keys():
                        new_value1 = res_dict[new_str1]
                    if new_str2 in res_dict.keys():
                        new_value2 = res_dict[new_str2]
                    if sli[1 - i] in new_value1 or sli[i-1] in new_value2:
                        if single_value in validSet:
                            validSet.remove(single_value)
            # A->[B,C],B->[C]
            if single_value in rel_dict.keys():
                two_lev = res_dict[single_value]
                for three_lev in two_lev:
                    if three_lev in value:
                        if three_lev in validSet:
                            validSet.remove(three_lev)
            
        res_dict[key] = validSet.copy()
        for rhs in validSet:
            fileout.write(key+'->'+rhs+"\n")
            vaildNumber += 1

    print(";;before: dependency number "+str(len(dependency_set)))
    print(";;after: dependency number "+str(vaildNumber))
    fileout.write(";;\n;;"+information[0]+"\n")
    fileout.write(";;before: dependency number "+str(len(dependency_set))+"\n")
    fileout.write(";;after: dependency number "+str(vaildNumber)+"\n")

if __name__=="__main__":
    pyMiningFile_path = sys.argv[1]
    tableId = sys.argv[2]
    start_time = time.time()
    filePath = pyMiningFile_path+"/result/dependency/dependency_result"+tableId+'.txt'
    # filePath = 'GED00.txt'
    fileout = open(filePath,'w',encoding='utf-8')
    readFile = pyMiningFile_path+"/test/process_3_producer/proTable_meaning/"+"produce_Table"+tableId+".txt"
    # readFile = "produce_Table0.txt"
    dependency_set = []
    information = []
    attriNumberLimit = int(sys.argv[3])
    # attriNumberLimit = -1
    mainMethod(readFile,dependency_set,information,attriNumberLimit)
    clean_redundant(dependency_set,fileout,information)
    end_time = time.time()
    print("start_time:", start_time)
    print("end_time:", end_time)
    print("time cost:", end_time - start_time, "s")
    fileout.write(";;time cost: "+str(end_time - start_time)+" s")
    fileout.close() 