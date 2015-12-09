import random
import copy
import collections
import numpy
from munkres import Munkres, print_matrix

def generateNormalDistData(n, p, k):
  data = [[0 for x in range(p)] for x in range(n)]
  negLimit = (-1*p)
  for i in range(len(data)):
    arr = range(p)
    rands = numpy.random.normal(0, p/2, p*100)
    #print rands
    doneTillNow = {}

    numPos = 0
    numNeg = 0
    done = False


    for j in range(len(rands)):
      if rands[j] > p or rands[j] < negLimit:
        continue
      if (rands[j] > 0):
        if numPos == k:
          continue
        val = int(rands[j])
        if val < 0 or val > p:
          continue
        if val in doneTillNow:
          continue
        else:
          #print "+1", val, rands[j]
          data[i][val] = 1
          doneTillNow[val] = True
          numPos += 1
      elif rands[j] < 0:
        if numNeg == k:
          continue
        val = int(p + rands[j])
        if val < 0 or val > p:
          continue
        if val in doneTillNow:
          continue
        else:
          #print "-1", val, rands[j]
          data[i][val] = -1
          doneTillNow[val] = True
          numNeg += 1
      if numPos == k and numNeg == k:
        #print "Done at ", j
        break

    for j in range(p):
      if j not in doneTillNow:
        if numPos < k:
          data[i][j] = 1
          numPos += 1
        elif numNeg < k:
          data[i][j] = -1
          numNeg += 1
        else:
          data[i][j] = 0
  return data

def generateRandomDistData(n, p, k):
  return generateNormalDistData(n, p, k)
  data = [[0 for x in range(p)] for x in range(n)]
  for i in range(len(data)):
    arr = range(p)
    random.shuffle(arr)
    for j in range(len(arr)):
      if j < k:
        data[i][arr[j]] = 1
      elif j > p - k - 1:
        data[i][arr[j]] = -1
      else:
        data[i][arr[j]] = 0
  return data

def baselineRandom(data):
  n = [x for x in range(len(data))]
  assign = [-1 for x in range(len(data))]
  random.shuffle(n)
  projects = [0 for y in range(len(data[0]))]
  projectsAssigned = {}
  for i in n:
    done = False
    for j in range(len(projects)):
      if data[i][j] == 1 and j not in projectsAssigned:
        assign[i] = j
        projectsAssigned[j] = True
        done = True
        break
    if done:
      continue

    for j in range(len(projects)):
      if data[i][j] == 0 and j not in projectsAssigned:
        assign[i] = j
        projectsAssigned[j] = True
        done = True
        break
    if done:
      continue

    for j in range(len(projects)):
      if data[i][j] == -1 and j not in projectsAssigned:
        assign[i] = j
        projectsAssigned[j] = True
        break
  return assign

def munkresAssign(d, m):
  data = copy.deepcopy(d)

  n = len(data)
  p = len(data[0])

  for i in range(n):
    for j in range(p):
      if data[i][j] == 1:
        data[i][j] = 1
      elif data[i][j] == 0:
        data[i][j] = n+1
      else:
        data[i][j] = (2*n)+1
  if n != p:
    x = p - n
    for i in range(x):
      dummy = [(2*n)+1 for x in range(p)]
      data.append(dummy)

  indices = m.compute(data)
  # print indices
  assign = [0 for x in range(n)]
  for row, col in indices:
    if row < n:
      assign[row] = col
  return assign

def getScore(data, assign):
  result = {}
  result[1] = 0
  result[0] = 0
  result[-1] = 0

  for i in range(len(assign)):
    if data[i][assign[i]] == 1:
      result[1] += 1
    elif data[i][assign[i]] == 0:
      result[0] += 1
    else:
      result[-1] += 1
  return result

if __name__ == "__main__":
  # random.seed(0)
  n = 25
  p = 25 
  k = 1

  # data = generateRandomDistData(n, p, k)
  # for each in data:
  #   print each

  # assign = munkresAssign(data, m)
  # score = getScore(data, assign)
  # print score


  baselineForRandomScores = {}
  munkresForRandomScores = {}
  iterations = 100
  divide = iterations*n

  mun = Munkres()

  # print "Num Preferences = k ::  POS     NEU     NEG"
  for k in range(12):
    bPos = 0.0
    bNeu = 0.0
    bNeg = 0.0
    
    mPos = 0.0
    mNeu = 0.0
    mNeg = 0.0
    for num in range(iterations):
      data = generateRandomDistData(n, p, k + 1)
      
      assign = baselineRandom(data)
      #print assign
      score = getScore(data, assign)
      bPos += score[1]
      bNeu += score[0]
      bNeg += score[-1]

      assign = munkresAssign(data, mun)
      score = getScore(data, assign)
      score = getScore(data, assign)
      mPos += score[1]
      mNeu += score[0]
      mNeg += score[-1]      
    #print "Num Preferences =", k, ":: ", pos/divide, "\t", neu/divide, "\t", neg/divide
    baselineForRandomScores[k] = (bPos/divide, bNeu/divide, bNeg/divide)
    munkresForRandomScores[k] = (mPos/divide, mNeu/divide, mNeg/divide)
  
  baselineForRandomScores = collections.OrderedDict(sorted(baselineForRandomScores.items()))
  munkresForRandomScores = collections.OrderedDict(sorted(munkresForRandomScores.items()))


  f = open("results1.csv", 'w')
  f.write("Vary Num Preferences\n\n")
  f.write("Baseline for Random Distribution\n\n")
  f.write("Number Of Preferences (k) , P(Positive), P(Neutral), P(Negative)\n")
  for k, v in baselineForRandomScores.iteritems():
    print k, v
    f.write((str(k+1) + ", " + str(v[0]) + ", " + str(v[1]) + ", " + str(v[2]) + "\n"))

  print
  f.write("\n\n\n")

  f.write("Munkres for Random Distribution\n\n")
  f.write("Number Of Preferences (k) , P(Positive), P(Neutral), P(Negative)\n")
  for k, v in munkresForRandomScores.iteritems():
    print k, v
    f.write((str(k+1) + ", " + str(v[0]) + ", " + str(v[1]) + ", " + str(v[2]) + "\n"))
  print
  f.write("\n\n\n")

  baselineForRandomScores = {}
  munkresForRandomScores = {}
  k = 5
  for m in range(25):
    bPos = 0.0
    bNeu = 0.0
    bNeg = 0.0
    
    mPos = 0.0
    mNeu = 0.0
    mNeg = 0.0
    for num in range(iterations):
      data = generateRandomDistData(n, p + m, k)
      
      assign = baselineRandom(data)
      #print assign
      score = getScore(data, assign)
      bPos += score[1]
      bNeu += score[0]
      bNeg += score[-1]

      assign = munkresAssign(data, mun)
      score = getScore(data, assign)
      score = getScore(data, assign)
      mPos += score[1]
      mNeu += score[0]
      mNeg += score[-1]      
    #print "Num Preferences =", k, ":: ", pos/divide, "\t", neu/divide, "\t", neg/divide
    baselineForRandomScores[n + m] = (bPos/divide, bNeu/divide, bNeg/divide)
    munkresForRandomScores[n + m] = (mPos/divide, mNeu/divide, mNeg/divide)

  baselineForRandomScores = collections.OrderedDict(sorted(baselineForRandomScores.items()))
  munkresForRandomScores = collections.OrderedDict(sorted(munkresForRandomScores.items()))

  f.write("Vary Num Projects\n\n")
  f.write("Baseline for Random Distribution\n\n")
  f.write("Number Of Projects (N + m), P(Positive), P(Neutral), P(Negative)\n")
  for k, v in baselineForRandomScores.iteritems():
    print k, v
    f.write((str(k) + ", " + str(v[0]) + ", " + str(v[1]) + ", " + str(v[2]) + "\n"))

  print
  f.write("\n\n\n")

  f.write("Munkres for Random Distribution\n\n")
  f.write("Number Of Projects (N + m), P(Positive), P(Neutral), P(Negative)\n")
  for k, v in munkresForRandomScores.iteritems():
    print k, v
    f.write((str(k) + ", " + str(v[0]) + ", " + str(v[1]) + ", " + str(v[2]) + "\n"))

  f.close()
  # print "Positive = ", score[1]
  # print "Neutral  = ", score[0]
  # print "Negative = ", score[-1]