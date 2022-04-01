#!/usr/bin/env python3
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 1.0a
# Description: This package contains different custom data types to make our lives easier. View the README for more info

from __future__ import annotations

import logging
import traceback
from difflib import get_close_matches as fmatch
from collections import defaultdict, Counter
from argparse import Namespace
from typing import Hashable, Any, Union, Optional, List, Tuple, Type, Iterable, Dict


VERSION = '1.0a'


# logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)s %(message)s',
#                     level=logging.INFO)
log = logging.getLogger('CustomDataStructures')


class FrozenDict(dict):

    def __hash__(self):
        """ This is here to make the Dict hashable. Normally it is not and simply adding this magic function doesn't
            mean that the dict is hashable. Making the dict immutable helps to make this hashable accurate.
        - :return:
        """

        return hash(self.__str__())

    @staticmethod
    def _readonly(*args, **kwards):
        """ Oh the fun. This is a custom class that is set below it to override all other functions that could possibly
            change the state of the data.
        - :param args:
        - :param kwards:
        - :return:
        """

        raise TypeError("Cannot modify Immutable Instance")

    __delattr__ = __setattr__ = __setitem__ = pop = update = setdefault = clear = popitem = _readonly


class KeyedList(list):
    """ <a name="KeyedList"></a>
        KeyedList is designed to act like a Table. A list of lists where it's rows are numbered and its columns are
        named. KeyedList achieves this by use of a Class variable of type dict alled 'template'. It overrides the
        __getitem__ (ie: []) magic function. The dict template values are simply ints that represent a position
        in each item on the KeyedList. For example: a template of {'ID': 0} means that: KeyedList['ID'] would return
        all the values of item[0] in its list.

        :var columns: A dictionary. Its values MUST BE INTEGERS
    """

    columns: dict = {}

    def __init__(self, *args, values: Optional[Iterable] = None, columns: Optional[Dict] = None):
        self.columns = columns or {}
        if values:
            super().__init__(values)
        else:
            super().__init__(*args)

    def __getitem__(self, item: Union[Hashable, int]) -> List:
        """ This is overridden from list. It adds the feature of handling keys like a dictionary.

        - :param item:
        - :return: A new KeyedList list
        """
        # print(f"item: {type(item)}")
        if type(item) == int or type(item) == slice:
            return super().__getitem__(item)
        tempInt = self.columns[item]
        return [value[tempInt] for value in self if len(value) > tempInt]

    def reset(self) -> None:
        """ This empties the list but doesn't empty the template.
        - :return: None
        """

        self[:] = []

    def get(self, item: Union[Hashable, int], default: Optional[Any] = None) -> Union[List, Any]:
        """ Return a list of items in the column identified by the 'item' parameter.

        - :param item: (Hashable) This is passed to the 'get' method of the template object variable which is a dict.
            The template should be a dictionary where its values are column numbers. The returning int from the 'get'
            method is used as the index value on all rows within the KeyedList to create and return a new list.
        - :param default: If the template doesn't have the item in its keys then this function will return this value.
        - :return: List or None
        """

        try:
            tempInt = self.columns.get(item)
            if tempInt is None:
                tempInt = int(item)
        except:
            return default
        return [value[tempInt] for value in self if len(value) > tempInt]

    def getColumn(self, col: Union[Hashable, int], default: Optional[Any] = None) -> Union[List, Any]:
        """ Return a list of items in the column identified by the 'item' parameter.

        - :param col: (Hashable or int) This is passed to the 'get' method of the template object variable which is a
            dict. The template should be a dictionary where its values are column numbers. The returning int from the
            'get' method is used as the index value on all rows within the KeyedList to create and return a new list.
        - :param default: If the template doesn't have the item in its keys then this function will return this value.
        - :return: List or None
        """

        try:
            tempInt = self.columns.get(col)
            if tempInt is None:
                tempInt = int(col)
        except:
            return default

        def _buildListHelper(value):
            if len(value) > tempInt:
                return value[tempInt]
            else:
                return ''

        return [_buildListHelper(value) for value in self]

    def getRow(self, row: int, default: Optional[Any] = None) -> Union[List, Any]:
        """ Returns a row if the row exits or the default return value.

        - :param row: (int)
        - :param default: (None)
        - :return: List or default value
        """

        if len(self) < row:
            return self[row]
        else:
            return default

    def getCell(self, row: int, col: Union[Hashable, int], default: Optional[Any] = None) -> Union[List, Any]:
        """ This gets the value within a coordinate of row x col.

        - :param row: (int)
        - :param col: (Hashable or int)
        - :param default: (None)
        - :return: (default avlue)
        """

        if len(self) >= row:
            return default
        columns = self.getColumn(col)
        if type(columns) is list:
            return columns[row]
        else:
            return default

    def sort(self, *args, key: Optional[Any] = None, reverse: bool = False, keyType: Type[Any] = str) -> KeyedList:
        """ An overridden wrapper of list.sort. This adds the feature of 'keyType' and requires the use of 'key'.

        - :param key: This is either an int representing a position in each item of the list or it is a
            key inside template which holds the actual int position.
        - :param reverse: Same as list.sort
        - :param keyType: DEFAULT: str, This is a builtin type or callable object that can convert the value obtained
            via the key. For example if you pass an int and the key as 0 this will try to take the value of item[0] and
            convert it into an int for sorting.
        - :return: KeyedList (itself)
        """

        if key:
            if type(key) == int:
                super().sort(key=lambda x: keyType(x[key]), reverse=reverse)
            else:
                super().sort(key=lambda x: keyType(x[self.columns[key]]), reverse=reverse)
            return self
        else:
            super().sort(reverse=reverse)
            return self


class IndexList(KeyedList):
    """ <a name="IndexList"></a>
        IndexList: Inherits from KeyedList. Wraps around a dict called indexDict.
        Its purpose is to add the ability to index values passed to itself. Which in turn makes searching for values
        and doing getCorrelation super fast.

        - :var indexDict: A dictionary where its keys are uniq values that have been appended to the list and the value
            the index/position in the list where the value can be found.
    """

    indexDict: defaultdict = defaultdict(list)

    def __init__(self, values: Optional[IndexList, KeyedList, List] = None, columns: Optional[Dict] = None):
        """ Creates a new IndexList. I like to name mine il cuz I am cool. The params are all optional and are as
            follows.

        - :param values: If you want to added keys at the moment this object is created this is how you would do so.
        - :param template: The template value that gets passed to KeyedList
        - :return: nothing... duh!
        """

        self.indexDict = defaultdict(list)
        if isinstance(values, IndexList):
            super().__init__(values=values, columns=values.columns)
            self.indexDict = values.indexDict
        elif isinstance(values, KeyedList):
            super().__init__(values=values, columns=values.columns)
        elif values:
            super().__init__(columns=columns)
            self.extend(values)
        else:
            super().__init__(columns=columns)

    # Magic Functions!
    def __setitem__(self, index: int, item: Iterable) -> None:
        """ This is overridden because of the added Indexing feature. the '_setItem' which is called helps deal with
            the problem of keeping the indexDic in sync with the actual data.

        - :param index: (int) Same as list.__setitem__
        - :param item: (Iterable) Same as list.__setitem__
        - :return: None
        """

        return self._setItem(index, item)

    def __getitem__(self, key: Optional[Tuple, Hashable, int]) -> Any:
        """ This is a little confusion and verbose but basically the '__getitem__' magic function is whats called when
            brackets/[] are used. This is designed to handle str/tuple/int types.

        - :param key: (Tuple, Hashable, int) This has to either be a str/tuple/int
        - :return: Iterable or single item
        """

        if isinstance(key, tuple):
            return self._getItem(key)
        else:
            return super().__getitem__(key)

    def reset(self) -> None:
        """ This clears the variable 'indexDict' and replaces it with a fresh defaultdict(list).

        - :return: None
        """

        self.indexDict = defaultdict(list)
        super().reset()

    def sort(self,  *args, key: Optional[Any] = None, reverse: bool = False, keyType: Type[Any] = str) -> IndexList:
        """ Just like KeyedList except each time data is sorted the indexes have to be rebuild! Its a lot of overhead.
            To avoid this perhaps use sort only on small data sets of KeyedLists. For example first pull data from a
            getCorrelation or search and make that data a KeyedList and then sort. If you are working with 10s of
            thousands of lines that approach will be faster then calling this function directly.
            Another performance trick would be call sort from KeyedList directly. This will cause the indexDict to no
            longer be valid but if its the last thing you are doing and you do not need to do anything else who cares!

        - :param cmp: Same as list.sort
        - :param key: Same as KeyedList.sort
        - :param reverse: Same as list.sort
        - :param keyType: Same as KeyedList.sort
        - :return: IndexList
        """

        super().sort(key=key, reverse=reverse, keyType=keyType)
        self._rebuildKeys()
        return self

    def remove(self, value: Iterable) -> IndexList:
        try:
            super().remove(value)
            self._rebuildKeys()
        except Exception as e:
            log.error(f'[ERROR]: Error occurred while attempting to remove an item from the IndexList: {e}')
            log.debug(f'[DEBUG]: Trace for error while attempting to remove an item from the IndexList:: '
                      f'{traceback.format_exc()}')
            raise e
        return self

    # NOTE: If you append a value that is not hashable such as a list within a list then this will fail
    def append(self, value: Iterable) -> IndexList:
        """ This append function will return itself (the whole IndexList) on its success at adding new data or it will
            throw an exception

        - :param value: (Iterable) This can handle a wide range of data. It will return None if the data isn't format
                correctly. The rule of thumb though is to simply pass a dict.
        - :return:
        """

        self._appendItem(value)
        return self

    def insert(self, index: Union[Hashable, int], item: Dict) -> None:
        """ This acts like insert from List

        - :param index: (string or int)
        - :param item: (Dictionary)
        - :return: (None)
        """

        if type(item) is not dict:
            return
        return self._setItem(index, item)

    def extend(self, iterable: Iterable) -> None:
        """ This acts like extend from List

        - :param iterable: (Iterable)
        - :return: (None)
        """

        super().extend(iterable)
        self._rebuildKeys()

    # Main functions that add... well more functionality to this class.
    def hasValue(self, value: Hashable) -> bool:
        """ Searches explicitly for the value

        - :param value: Normally a string
        - :return: bool
        """

        return value in self.indexDict

    def hasPair(self, pair: Tuple) -> bool:
        """ Searches explicitly for the value in this (column, value) pair.

        - :param pair: Has to be a tuple!
        - :return: bool
        """
        if len(pair) != 2:
            return False
        return pair[-1] in self.getColumn(pair[0], default=[])

    def search(self, *args, matchCutoff: float = 0.6, explicit: bool = True,
               ignoreCase: bool = False, **kwargs) -> List:
        """ An implicit or explicit look up of all the values within the set.

        - :param args: each argument parameter should be a string or hashable
        - :param matchCutoff: (float) default 0.6. Used for fuzzy matching. This is only used if explicit is False
        - :param explicit: (bool) default True. If this is False matchCutoff is used to do a fuzzy match
        - :param ignoreCase: (bool) default False. This does as it says. It ignores case by making everything lowercase
        - :return: a List
        """

        number = len(self.indexDict)

        if type(matchCutoff) is not float:
            matchCutoff = 0.6
        elif matchCutoff < 0.0 or matchCutoff > 1.0:
            matchCutoff = 0.6
        if explicit:
            matchCutoff = 1.0

        def _searchHelper(value, compareValue):
            return len(fmatch(value.lower(), [compareValue.lower()], n=1, cutoff=matchCutoff)) > 0

        if ignoreCase:
            return [i for i in self.indexDict for value in args if _searchHelper(value, i)]
        else:
            return list(set([i for subl in
                             [fmatch(value, self.indexDict, n=number, cutoff=matchCutoff) for value in args]
                    for i in subl]))

    def searchColumn(self, col: Union[Hashable, int], value: str, matchCutoff: float = 0.6,
                     explicit: bool = True, ignoreCase: bool = False, **kwargs) -> List:
        """ Search a single column for a particular value.

        - :param col: (String or Int)
        - :param value: (searchable string)
        - :param matchCutoff: (float) Works just as it does in search. It is a fuzzy match.
        - :param explicit: (bool) default True. Works just as it does in search.
        - :param ignoreCase: (bool) default False. Works just as it does in search.
        - :param kwargs:
        - :return:
        """

        if type(matchCutoff) is not float:
            matchCutoff = 0.6
        elif matchCutoff < 0.0 or matchCutoff > 1.0:
            matchCutoff = 0.6
        if explicit:
            matchCutoff = 1.0

        values = self.getColumn(col)

        def _searchColumns(compareKey, compareValue):
            if ignoreCase:
                return len(fmatch(compareKey.lower(), [compareValue.lower()], n=1, cutoff=matchCutoff)) > 0
            else:
                return len(fmatch(compareKey, [compareValue], n=1, cutoff=matchCutoff)) > 0

        return [x for x in range(len(values)) if _searchColumns(compareKey=value, compareValue=values[x])]

    def searchColumns(self, *args, dedup: bool = False, intersect: bool = False, **kwargs) -> List:
        """ Using searchColumn this can take multiple columns and can also deduplicate index values or only show index
            values that are the same. Review 'searchColumn' documentation for more info.

        - :param args: REQUIRED: tuple, this is a tuple or multi tuples. The first value in the tuple is used as the
            col value while the second value is used as the value parameter in 'searchColumn'.
        - :param dedup: (bool)  default False. If true this will remove all duplicate index values.
        - :param intersect: (bool) default False. If true this will return only index values that show up more then once
        - :return: List of positions that the pair shows up in the list.
        """

        indexes = []
        pairs = []
        temp = tuple()
        for item in args:
            if type(item) is tuple:
                pairs.append(item)
            elif type(item) is str or type(item) is int:
                if len(temp) == 0:
                    temp = (item,)
                elif len(temp) == 1:
                    pairs.append((temp[0], item))
                    temp = tuple()

        for key in pairs:
            indexes.extend(self.searchColumn(col=key[0], value=key[1], **kwargs))

        if dedup:
            return list(set(indexes))
        if intersect:
            return [item for item, count in Counter(indexes).items() if count > 1]
        return indexes

    def getIncompleteLineSearch(self, *args, wordsLeft: float = 0.4, **kwargs) -> IndexList:
        """ Ok the idea behind this is to be able to do a getCorrelation without knowing if some
            items in the search list past to args actually exists or not. This function filters the search list passed
            in by args first and then correlates the data that is left.

        - :param args: This can be formatted as a single string with the phrase or each word in the phrase as an arg.
        - :param wordsLeft: (float) Default 0.4 or no less then 40% of the words left. Each word in the phrase is
            checked with 'hasValue' to see if it exists.
        - :return: IndexList
        """

        if type(wordsLeft) is not float:
            wordsLeft = 0.4
        elif wordsLeft < 0.0 or wordsLeft > 1.0:
            wordsLeft = 0.4

        if len(args) == 1:
            if type(args[0]) is str and len(args[0].strip().split()) > 1:
                args = args[0].strip().split()

        newSearchList = [value for value in args if self.hasValue(value)]
        if not newSearchList:
            return IndexList()

        lengthArgs = len(newSearchList)
        if lengthArgs < 2:
            return IndexList()

        if float(lengthArgs) / float(len(args)) < wordsLeft:
            return IndexList()

        return self.getCorrelation(*newSearchList, **kwargs)

    def getCorrelation(self, *args, **kwargs) -> IndexList:
        """ This is using the 'intersection' function from set under the hood. What it attempts to do is take all the
            data associated with each other by common variables and return them. This is achieved by pulled all data
            associated with each search type and then removing all duplicates and then only returning values that are
            the same. using intersection.

        - :param args: Currently this is just strings that can be passed. Multi strings.
        - :return: It returns a KeyedList of the data you want correlated
        """

        def _searchHelper(searchItem):
            if type(searchItem) is tuple:
                return self.searchColumns(searchItem, **kwargs)
            return self.search(searchItem, **kwargs)

        searches = [_searchHelper(search) for search in args]
        searchIndex = []
        for search in searches:
            tempList = []
            for key in search:
                if type(key) is int:
                    tempList.append(key)
                    continue
                tempList.extend([index for index in self.indexDict[key]])
            searchIndex.append(frozenset(tempList))

        searchesList = list(frozenset.intersection(*searchIndex))
        output = IndexList(columns=self.columns)

        if searchesList:
            searchesList.sort()
            output.extend([self[item] for item in searchesList])
        return output

    def getSearch(self, *args, **kwargs) -> IndexList:
        """ This function uses 'search' and 'searchColumns' to find values that are used to build a new IndexList. This
            is likely the most used method of this class.

        - :param args: Either a tuple or a str
        - :return: A KeyedList
        """

        output = IndexList(columns=self.columns)

        indexes = []
        values = []
        for item in args:
            if type(item) == tuple:
                indexes.append(item)
            else:
                values.append(item)

        kwargs.update({'dedup': True})
        indexes = self.searchColumns(*indexes, **kwargs)
        args = self.search(*values, **kwargs)

        if not args and not indexes:
            return output

        if args:
            indexes.extend(set([index for indexKey in args for index in self.indexDict[indexKey]]))
        indexes.sort()

        output.extend([super(IndexList, self).__getitem__(index) for index in indexes])

        return output

    # Private functions below
    def _getIndexesByValue(self, *args):
        output = []
        for key in args:
            output.extend([index for index in self.indexDict[key]])
        return output

    def _rebuildKeys(self):
        indexDict = defaultdict(list)
        num = 0
        for item in self:
            for value in item:
                indexDict[value].append(num)
            num += 1
        self.indexDict = indexDict
        return True

    def _appendItem(self, item: Iterable) -> bool:
        super(IndexList, self).append(item)
        num = (len(self) - 1)
        for value in item:
            self.indexDict[value].append(num)
        return True

    def _setItem(self, index: Union[Hashable, int], item: Dict) -> None:
        for key in super().__getitem__(index):
            self.indexDict[key].remove(index)
        for value in item:
            self.indexDict[value].append(index)
        return super().__setitem__(index, item)

    def _getItem(self, key: Tuple) -> KeyedList:
        indexValues = self[key[0]]
        indexes = [x for x in range(len(indexValues)) if indexValues[x] == key[-1]]
        if indexes:
            return KeyedList([self[index] for index in indexes], columns=self.columns)
        return KeyedList(columns=self.columns)

    @staticmethod
    def sortBySearch(searchList, otherList) -> Iterable:
        if type(searchList) is not list or isinstance(otherList, list):
            return []
        if not (len(otherList) > 0 and type(otherList[0] is list)):
            return []

        def _maxHelperFunc(*args):
            x = 0
            for item in searchList:
                if item in args:
                    x += 1
            return x

        if type(otherList) is IndexList:
            results = IndexList(columns=otherList.columns)
        elif type(otherList) is KeyedList:
            results = KeyedList(columns=otherList.columns)
        else:
            results = []

        for x in range(otherList):
            results.append(max(otherList, key=_maxHelperFunc()))

        return results


class NamespaceDict(Namespace):
    """
        This is a simple wrapper around the argparse Namespace class. It is meant to make the Namespace subscriptable
        like a dictionary. It attempts to copy all the dictionary functionality.
    """

    def __init__(self, *args, **kwargs):
        super(NamespaceDict, self).__init__(**kwargs)
        self.__hiddenDict = vars(self)

    def __iter__(self):
        return self.__hiddenDict.__iter__()

    def __getitem__(self, item):
        return self.__hiddenDict[item]

    def __setitem__(self, key, value):
        self.__hiddenDict[key] = value

    def __str__(self):
        return str(self.copy())

    def clear(self):
        self.__hiddenDict.clear()
        self.__hiddenDict = vars(self)

    def copy(self):
        newDict = self.__hiddenDict.copy()
        newDict.pop('_NamespaceDict__hiddenDict')
        return newDict

    def fromkeys(self, iterable, value=None):
        return self.__hiddenDict.fromkeys(iterable, value)

    def get(self, key, default=None):
        return self.__hiddenDict.get(key, default)

    def items(self):
        items = (item for item in self.__hiddenDict.items())
        next(items)
        return items

    def keys(self):
        key = (key for key in self.__hiddenDict.keys())
        next(key)
        return set(key)

    def pop(self, key):
        if len(self.__hiddenDict) == 1:
            item = self.__hiddenDict.pop(key)
            self.__hiddenDict = vars(self)
            return item
        return self.__hiddenDict.pop(key)

    def popitem(self):
        if len(self.__hiddenDict) == 1:
            item = self.__hiddenDict.popitem()
            self.__hiddenDict = vars(self)
            return item
        return self.__hiddenDict.popitem()

    def setdefault(self, key, default):
        return self.__hiddenDict.setdefault(key, default)

    def update(self, m, **kwargs):
        self.__hiddenDict.update(m, **kwargs)

    def values(self):
        value = (value for value in self.__hiddenDict.keys())
        next(value)
        return list(value)
