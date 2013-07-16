import json
import random

class loteryLearner(object):
    def __init__(self):
        self.result = {}
        self.result['total'] = 0
        self.result['first'] = {}
        self.result['special'] = {}
        self.result['next'] = {}
        for i in range(38):
            self.result['next'][i+1] = {}
            for j in range(38):
                self.result['next'][i+1][j+1] = 0
            self.result['first'][i+1] = 0
        for i in range(8):
            self.result['special'][i+1] = 0

    def learn(self, lstLearningData):
        for learningData in lstLearningData:
            with open(learningData,'r') as data:
                for line in data:                
                    self._learn_single(line)
        return self.result
        
    def _learn_single(self, strLine):
        self.result['total'] += 1
        raw = strLine.split(',')
        self.result['first'][int(raw[3])] += 1
        self.result['special'][int(raw[9])] += 1
        for i in (3,4,5,6,7):
            self.result['next'][int(raw[i])][int(raw[i+1])] += 1
        
class loteryPicker(object):
    #code
    def __init__(self, learnedData):
        self.learned = learnedData
        
    def _find_max(self, dicItems, count):
        sortedKeys = []
        for key, value in sorted(dicItems.iteritems(), key=lambda (k,v): (v,k)):
            sortedKeys.append(key)
        #return sortedKeys[-1*count:] #return most appear
        return sortedKeys[:count] #return least appear
    
    def _build_number_list(self, item):
        res = []
        while item['parent']:
            item = item['parent']
            res.append(item['number'])
        return res
        
    def _recursive_get_next(self, item, currentOrder, order, count):
        if currentOrder > order:
            count = 1
        if currentOrder > 5:
            return
        else:
            item['next'] = []
        lstCurrentNumber = self._build_number_list({'parent':item})
        prob = self.learned['next'][item['number']].copy()
        for key in lstCurrentNumber:
            prob.pop(key)
        lstNext = self._find_max(prob, count)
        for intNext in lstNext:
            subItem = {'parent':item, 'number':intNext, 'next':None}
            item['next'].append(subItem)
            self._recursive_get_next(subItem, currentOrder+1, order, count)
    
    def _recursive_build_number_list(self, item, lstRes):
        if item['next'] == None:
            res = []
            while item:
                res.append(item['number'])
                item = item['parent']
            lstRes.append(res[::-1])
        else:
            for subItem in item['next']:
                self._recursive_build_number_list(subItem, lstRes)
    
    def pick(self, order = 4, count = 3):
        res = []
        lstOp = []
        lstFirst = self._find_max(self.learned['first'], count)
        for first in lstFirst:
            item = {'parent':None, 'number':first, 'next':None}
            res.append(item)
            self._recursive_get_next(item, 1+1, order, count)
        ret = []
        for item in res:
            self._recursive_build_number_list(item, ret)
        for numberList in ret:
            prob = self.learned['special'].copy()
            lstSpecial = self._find_max(prob, count)
            numberList.append(lstSpecial[0])
        return ret

class loteryVerifier(object):
    def verify(self, lstVerifyData, lstPicked):
        totals = {}
        for verifyData in lstVerifyData:        
            with open(verifyData) as verify:
                for line in verify:
                    total = 0
                    arr = line.split(',')
                    ordinary = []
                    for number in arr[3:9]:
                        ordinary.append(int(number))
                    #print ordinary
                    special = int(arr[9])
                    #print special
                    for numbers in lstPicked:
                        count = 0
                        sp = 0
                        for number in numbers:
                            if number in ordinary:
                                count += 1
                        if numbers[-1] == special:
                            sp = 1

                        if count == 6 and sp == 1:
                            print str(numbers)+' holly shit.'
                        elif count == 6:
                            print str(numbers)+' shit.'
                        elif count == 5 and sp == 1:
                            total += 150000
                        elif count == 5:
                            total += 20000
                        elif count == 4 and sp == 1:
                            total += 4000
                        elif count == 4:
                            total += 800
                        elif count == 3 and sp == 1:
                            total += 400
                        elif count == 3:
                            total += 100
                        elif count == 2 and sp == 1:
                            total += 200
                        elif count == 1 and sp == 1:
                            total += 100
                        #if count > 4 or (sp == 1 and count > 0):
                        #    total += 1
                    #print 'game: '+arr[-1][:-1]+', earned: '+str(total)
                    totals[arr[-1][:-1]] = total
        return totals

class randomPicker(object):
    def __init__(self):
        self.numbers = range(1, 39)
        self.specials = range(1, 9)

    def _shuffle(self, count):
        for i in range(count):
            rand1 = int(random.random()*38)
            rand2 = int(random.random()*38)
            self.numbers[rand1], self.numbers[rand2] = self.numbers[rand2], self.numbers[rand1]
            rand1 = int(random.random()*8)
            rand2 = int(random.random()*8)
            self.specials[rand1], self.specials[rand2] = self.specials[rand2], self.specials[rand1]
    def pick(self, count):
        res = []
        for i in range(count):
            self._shuffle(100)
            numbers = self.numbers[:6]
            numbers.append(self.specials[0])
            res.append(numbers)
        return res


if __name__ == '__main__':
    learner = loteryLearner()
    result = learner.learn(['..\\data\\2008.csv','..\\data\\2009.csv','..\\data\\2010.csv','..\\data\\2011.csv','..\\data\\2012.csv'])
    with open('res.txt','w') as res:
        res.write(json.dumps(result))
    picker = loteryPicker(result)
    rPicker = randomPicker()
    lstKerker = picker.pick(2,5)
    count = len(lstKerker)
    for numbers in lstKerker:
        print numbers
    lstRand = rPicker.pick(count)
    print 'spent: '+str(100*len(lstKerker)) + ' per game.'
    #print lstKerker
    verifier = loteryVerifier()
    totals = verifier.verify(['..\\data\\2013.csv'],lstKerker)
    wins = []
    for key in totals.keys():
        if totals[key] > 100*len(lstKerker):
            wins.append(totals[key])
    print 'win '+ str(len(wins))+ ', max: '+ str(max(wins))
    print '================'
    #totals = verifier.verify(['..\\data\\2013.csv'],lstRand)
    for i in range(20):
        beat = 0
        lstRand = rPicker.pick(count)
        rTotals = verifier.verify(['..\\data\\2013.csv'],lstRand)
        rwins = []
        for key in totals.keys():
            if totals[key] > rTotals[key]:
                beat += 1
            if rTotals[key] > 100*len(lstKerker):
                rwins.append(rTotals[key])
        try:
            print 'run ' + str(i) + ', rwin '+ str(len(rwins))+ ', max: '+ str(max(rwins))
        except:
            print 'run ' + str(i) + ', rwin '+ str(len(rwins))
        #print 'run ' + str(i) + ', beat random ' + str(beat) + ' times in ' + str(len(totals.keys())) + ' games.'