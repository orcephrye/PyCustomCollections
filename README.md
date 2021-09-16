# Custom Data Package

This package is meant to help parse large amounts of text from log files and command output. 

### Requirements
```bash
python3 -m pip install --upgrade difflib
```

There are 3 classes within CustomDataPackage. FrozenDict, KeyedList, IndexList. 

- FrozenDict: is a simple hashable readonly version of the standard 'dict' Python class.
- KeyedList: This class inherites the standard 'list' Python class. It wraps a 'dict' called columns which uses a 
    hashable value as a key and the value is an index number. This behaves more like a table and allows the user to look
    up columns or rows.
- IndexList: This inherites KeyedList but also indexes all words into a 'dict' named indexDict. These variables are 
    used to search and correlate data. This class is used to quickly search for words as well as individual lines.
    
#### Examples for KeyedList:

Creating a simple KeyedList:
```python
from CustomDataPackage import KeyedList
kl1 = KeyedList(columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
print(kl1.columns)
# OUTPUT: {'ID': 0, 'Name': 1, 'SuperPower': 2}
```
Adding data too this KeyedList:
```python
from CustomDataPackage import KeyedList
kl1 = KeyedList(columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
kl1.append(["133", "Joey", "Jumping Jacks"])
kl1.append(["122", "Tim", "Lazer Eyes"])
# OR Alternative creation method
kl1 = KeyedList([['133', 'Joey', 'Jumping Jacks'], ['122', 'Tim', 'Lazer Eyes']], columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
print(kl1)
# OUTPUT: [['133', 'Joey', 'Jumping Jacks'], ['122', 'Tim', 'Lazer Eyes']]
print(kl1['ID'])
# OUTPUT: ['133', '122']
```
Just like a List KeyedList also supports sorting except it can use columns.
```python
from CustomDataPackage import KeyedList
kl1 = KeyedList([['133', 'Joey', 'Jumping Jacks'], ['122', 'Tim', 'Lazer Eyes']], columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
print(kl1)
# OUTPUT: [['133', 'Joey', 'Jumping Jacks'], ['122', 'Tim', 'Lazer Eyes']]
kl1.sort(key='ID', keyType=int)
print(kl1)
# OUTPUT: [['122', 'Tim', 'Lazer Eyes'], ['133', 'Joey', 'Jumping Jacks']]
```

#### Examples for IndexList:

Creating a simple IndexList:
```python
from CustomDataStructures import IndexList 
il1 = IndexList(columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
il1.extend( [['133', 'Joey', 'Jumping Jacks'],
 ['122', 'Tim', 'Lazer Eyes'],
 ['144', 'Ryan', 'Crazyness'],
 ['133', 'Ryan', 'Flight']] )
print(il1.indexDict)
# OUTPUT: defaultdict(<class 'list'>, {'133': [0, 3], 'Joey': [0], 'Jumping Jacks': [0], '122': [1], 'Tim': [1], 'Lazer Eyes': [1], '144': [2], 'Ryan': [2, 3], 'Crazyness': [2], 'Flight': [3]})
```

Using the 'search' methods.
```python
from CustomDataStructures import IndexList 
il1 = IndexList(columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
il1.extend( [['133', 'Joey', 'Jumping Jacks'],
 ['122', 'Tim', 'Lazer Eyes'],
 ['144', 'Ryan', 'Crazyness'],
 ['133', 'Ryan', 'Flight']] )
# All searches are explicit by default. 
il1.search('tim')
# OUTPUT: []
il1.search('tim', explicit=False)
# OUTPUT: ['Tim']
# You can ignore case.
il1.search('ryan', ignoreCase=True)
# OUTPUT: ['Ryan']
# You can change the 'fuzzyness' of the match. Default is 0.6
il1.search('crazy', explicit=False, matchCutoff=0.6)
# OUTPUT: []
il1.search('crazy', explicit=False, matchCutoff=0.5)
# OUTPUT: ['Crazyness']
# 'searchColumn' examples. 'searchColumn' is different in many ways. Most notability it returns index values.
il1.searchColumn(col='ID', value='133')
# OUTPUT: [0, 3]
print(il1[0])
# OUTPUT: ['133', 'Joey', 'Jumping Jacks']
# Just with search this is explicit by default and ignoreCase is false by default and use of matchCutoff.
il1.searchColumn(col='SuperPower', value='crazy')
# OUTPUT: []
il1.searchColumn(col='SuperPower', value='crazy', explicit=False, matchCutoff=0.5)
# OUTPUT: [2]
print(il1[2])
# OUTPUT: ['144', 'Ryan', 'Crazyness']
# Method 'searchColumns' allows to search values across multiple columns.
il1.searchColumns(('ID', '133'), ('SuperPower', 'Flight'))
# OUTPUT: [0, 3, 3]
# 'searchColumns' can also deduplicate results or only return results that have duplicate entries.
il1.searchColumns(('ID', '133'), ('SuperPower', 'Flight'), dedup=True)
# OUTPUT: [0, 3]
il1.searchColumns(('ID', '133'), ('SuperPower', 'Flight'), intersect=True)
# OUTPUT: [3]
```

Using the 'getColumn' method and how it differs from "il1['ID']" magic lookup. This shows that IndexList doesn't care
if data is formatted with the same number of columns. It also shows that the 'getColumn' should be used in case 
data is not formatted correctly. This is really useful when dealing with log file entries. 'getRow' and 'getCell' 
also gracefully handle erratically formatted data. These 3 functions also all act like 'get' method from 'dict' in that
they also have a 'default' parameter which is what is returned when nothing is found. Other 'get' methods are 'search'
methods and are explained below.
```python
from CustomDataStructures import IndexList 
il1 = IndexList(columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
il1.extend( [['133', 'Joey', 'Jumping Jacks'],
 ['122', 'Tim', 'Lazer Eyes'],
 ['144', 'Ryan', 'Crazyness'],
 ['133', 'Ryan', 'Flight'], 
 ['155', 'Phil'], 
 ['166', 'John', 'Strength', 'Health']] )
# Notice how there is now two new entries that both do not have the same number of columns. 
il1['SuperPower']
# OUTPUT: ['Jumping Jacks', 'Lazer Eyes', 'Crazyness', 'Flight', 'Strength']
il1.getColumn('SuperPower')
# OUTPUT: ['Jumping Jacks', 'Lazer Eyes', 'Crazyness', 'Flight', '', 'Strength']
il1.getColumn(3)
# OUTPUT: ['', '', '', '', '', 'Health']
```

Using the 'get' search methods. These methods all start with 'get'. All these methods return a new IndexList with the
same columns dict. The exceptions are 'getColumn', 'getRow', 'getCell' which is explained above.
```python
from CustomDataStructures import IndexList 
il1 = IndexList(columns={'ID': 0, 'Name': 1, 'SuperPower': 2})
il1.extend( [['133', 'Joey', 'Jumping Jacks'],
 ['122', 'Tim', 'Lazer Eyes'],
 ['144', 'Ryan', 'Crazyness'],
 ['133', 'Ryan', 'Flight']] )
il2 = il1.getSearch('Tim')
print(il2['Name'])
# OUTPUT: ['Tim']
# getSearch is a powerful method that can take both tuples and individual search values and thus uses 'search' and 
# 'searchColumn'. And as always this means that parameters 'explicit' and 'ignoreCase' are usesable.
il1.getSearch(('ID', '133'), 'tim', ignoreCase=True)
# OUTPUT: [['133', 'Joey', 'Jumping Jacks'],
# ['122', 'Tim', 'Lazer Eyes'],
# ['133', 'Ryan', 'Flight']]
# The 'getCorrelation' search returns an IndexList with only entries match all parameters. Think of 'getSearch' as "OR"
# while 'getCorrelation' is "AND". Notice how both Ryan and Joey have the same ID? 
il1.getSearch(('ID', '133'))
# OUTPUT: [['133', 'Joey', 'Jumping Jacks'], ['133', 'Ryan', 'Flight']]
il1.getCorrelation('133', 'Ryan')
# OUTPUT: [['133', 'Ryan', 'Flight']]
# The 'getIncompleteLineSearch' uses a single line of text to search for whole rows that loosely match that line. Other
# way too think of it is searching for lines of text using a phrase. There is a parameter 'wordsLeft' that works just 
# like matchCutoff (which is also uses in this method) to determine how many words within the phrase are needed to make
# a match. This works really well when searching log entries.
il1.getIncompleteLineSearch('Ryan Flight')
# OUTPUT: [['133', 'Ryan', 'Flight']]
```


 Simple, quick, powerful.
