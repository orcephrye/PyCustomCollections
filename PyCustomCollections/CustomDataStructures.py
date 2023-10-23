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
from typing import Hashable, Any, Union, Optional, List, Tuple, Type, Iterable, Dict, Callable


VERSION = '1.0a'


# logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)s %(message)s',
#                     level=logging.INFO)
log = logging.getLogger('CustomDataStructures')


def dummy_func(*args, **kwargs):
    return kwargs.get('_default', None)


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

        .. deprecated:: 1.0a
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
        and doing getCorrelation superfast.

        - :var indexDict: A dictionary where its keys are uniq values that have been appended to the list and the value
            the index/position in the list where the value can be found.

        .. deprecated:: 1.0a
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

        if values:
            return [x for x in range(len(values)) if _searchColumns(compareKey=value, compareValue=values[x])]
        return []

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


class KeyedTable(list):
    """ <a name="KeyedTable"></a>
        KeyedTable is designed to act like a Table. A list of lists where it's rows are numbered and its columns are
        named. KeyedList achieves this by use of a class variable of type dict called 'columns'. It overrides the
        __getitem__ (ie: []) magic function to make the class subscriptable. The dict template values are ints that
        represent a position in each item on the KeyedList. For example: a template of {'ID': 0} means that:
        KeyedList['ID'] would return all the values of item[0] in its list or [item[0] for item in self].

        :var columns: A dictionary. Its values MUST BE INTEGERS
    """

    columns: dict = None

    def __init__(self, *args, columns: Optional[Dict] = None):
        self.columns = columns or {}
        if len([value for value in self.columns.values() if type(value) != int]) > 0:
            raise TypeError('The columns dictionary values must be integers')
        super().__init__(*args)

    def __getitem__(self, item: Union[Hashable, slice]) -> list:
        """ This override is meant to make this class subscriptable and thus item can more than just int/slice """
        if isinstance(item, (int, slice)):
            return super().__getitem__(item)
        if not isinstance(item, str):
            raise TypeError(f'KeyedTable indices must be either integers, slices or strings not {type(item)}')
        if not self.columns and item.isdigit():
            indices = int(item)
        else:
            indices = self.columns[item]
        return [value[indices] for value in self]

    def get(self, item: Hashable, default: Any = None) -> Union[list, Any]:
        """ This attempts to emulate the dictionary 'get' method behavior. It will use the 'item' to do a get on the
            'columns' class variable which if exists will return an integer value representing the column number.
            This function will then iterator through the KeyedTable list row by row and build a new list from the
            specified column number. Or it will return the specified default.

        :param item: (Hashable type) This is usually a string. If the KeyedTable isn't provided with a columns
            dictionary this item can still be an string representable: IE: '1' and this will still work.
        :param default: The value to return if the item is not in 'columns' or item.isdigit() is False.
        :return: list or default
        """

        try:
            if not self.columns and isinstance(item, str) and item.isdigit():
                index = int(item)
            else:
                index = self.columns[item]
        except:
            return default
        return [value[index] for value in self]

    def get_cell(self, row: int, col: Hashable, default: Any = None) -> Any:
        """ This requires a row specified by an integer and a column specified by a Hashable (usually str) type.
            This also attempts to emulate the dictionary 'get' method behavior in teh same way KeyedList's 'get'
            method does.

        :param row: (int) This is the row number
        :param col: (Hashable) usually a string
        :param default: The value to return the row/col cannot be found
        :return: list or default
        """

        if len(self) < abs(row):
            return default
        if not self.columns and isinstance(col, str) and col.isdigit():
            return self[row][self.columns[int(col)]]
        elif col not in self.columns:
            return default
        return self[row][self.columns[col]]

    def iter_column(self, col: Hashable, default: Any = ()) -> Union[Iterable, Any]:
        """ Again this has the 'default' parameter which helps this method behave like a dictionary's 'get' method in
            the same way that KeyedList's 'get' method does. This is ment to make it efficient to iterate over any
            column in the dataset.

        :param col: (Hashable) used to look into the 'columns' dictionary
        :param default: The value to return if the col variable is not in columns.
        :return: iterator
        """

        try:
            if not self.columns and isinstance(col, str) and col.isdigit():
                indices = int(col)
            else:
                indices = self.columns[col]
        except:
            return default
        return (value[indices] for value in self)

    def iter_row(self, row: int, default: Any = ()) -> Union[Iterable, Any]:
        """ Again this has the 'default' parameter which helps this method behave like a dictionary's 'get' method in
            the same way that KeyedList's 'get' method does. This is ment to make it easy to iterator over a
            specified row. Usually only necessary if the rows in the data are massive.

        :param row: (int) used to specify the row
        :param default: The value to return if the row to big
        :return: iterator
        """

        if len(self) < abs(row):
            return default
        return (item for item in self[row])

    def sort_by_column(self, column: Hashable, column_type: Callable, reverse: bool = False) -> None:
        """ A special version of the builtin sort method in List. This is used to take advantage of the keyed/labeled
            columns in the KeyedTable. There are no safety built into this function and it can raise an exception
            if the wrong column or column_type is provided.

        :param column: (Hashable)
        :param column_type: (Callable) a type such as int or str or any object that is callable that can convert its
            args into something usable as a key in sort.
        :param reverse: Same as reverse in List's 'sort' method.
        :return: None
        """

        super().sort(key=lambda x: column_type(x[self.columns[column]]), reverse=reverse)


class IndexedTable(KeyedTable):
    """ <a name="IndexedTable"></a>
        IndexedTable: Inherits from KeyedTable. Its purpose is to add the ability to index values passed to itself.
        Which in turn makes searching for values and row/columns between O(1) ie: constant to O(n log(n)) slightly
        above linear.

        This class attempts to follow a standard of naming methods. There are 'has_', 'indices_of_', 'fuzzy_' and
        the primary search functions, 'search', 'search_by_column', 'correlation'. Each of the primary search functions
        are matched with a fuzzy_ version and 'indices_of_'. The 'has_' methods always return bools. The 'indices_of_'
        always return iterators of ints.

        Here are the common parameters found in most methods and there default values:
        explicit=True | ignore_case=False | ordered=True | convert=True | similarity=0.6

        * explicit: This implies the lookup wil do a '=='. IE: key == item. When False it does: key in item.
        * ignore_case: When True this will do a 'lower()' on the value in question, this assumes string, on both the
            key and item before the comparison.
        * ordered: This will take the indices' data, which should be in a set and convert it into a list then run sort
            on it.
        * convert: This will always return a new IndexedTable, even if empty, unless it is false then it will return
            a list.
        * similarity: This is only associated with fuzzy methods and is an indication as to how similar the keyword
            needs to be to the item.

        The default values for explicit, ignore_case, ordered, and convert can be changed on init.

    """

    def __init__(self, *args, columns: Optional[Dict] = None,
                 explicit: bool = True, ignore_case: bool = False, ordered: bool = True, convert: bool = True):
        self.explicit = explicit
        self.ignore_case = ignore_case
        self.ordered = ordered
        self.convert = convert
        self.__index = defaultdict(set)
        if len(args) == 1 and isinstance(args[0], (IndexedTable, KeyedTable)):
            super().__init__(*args, columns=args[0].columns)
            self.__index = getattr(args[0], 'index', defaultdict(set))
        else:
            super().__init__(*args, columns=columns)
        if len(self) > 0:
            self.build_index()

    def __str__(self):
        return '\n'.join((' '.join(item) for item in self))

    def build_index(self, rebuild=True) -> None:
        """ This builds the Index using a 'hidden' variable '__index' which is a defaultdict whose values are sets """
        if self.__index:
            if rebuild:
                self.__index = defaultdict(set)
            else:
                return None

        for i, items in enumerate(self):
            for item in items:
                self.__index[item].add(i)

    def has_value(self, value: Hashable, **kwargs) -> bool:
        """ Returns true if the value exists within the index. """
        explicit, ignore_case = self._processKwargs('explicit', 'ignore_case', **kwargs)
        if explicit is True and ignore_case is False:
            return value in self.__index
        if explicit is True and ignore_case is True:
            value = getattr(value, 'lower', dummy_func)()
            for item in self.__index:
                if value == getattr(item, 'lower', dummy_func)():
                    return True
            return False
        if explicit is False and ignore_case is False:
            for item in self.__index:
                if value in item:
                    return True
            return False
        if explicit is False and ignore_case is True:
            value = getattr(value, 'lower', dummy_func)()
            for item in self.__index:
                if value in getattr(item, 'lower', dummy_func)():
                    return True
            return False

    def has_pair(self, column, value, **kwargs) -> bool:
        """ Looks for a value within a column and returns True if it exists """
        explicit, ignore_case = self._processKwargs('explicit', 'ignore_case', **kwargs)
        if explicit is True and ignore_case is False:
            if value not in self.__index:
                return False
            for item in self.iter_column(column):
                if value == item:
                    return True
            return False
        if explicit is True and ignore_case is True:
            value = getattr(value, 'lower', dummy_func)()
            for item in self.iter_column(column):
                if value == getattr(item, 'lower', dummy_func)():
                    return True
            return False
        if explicit is False and ignore_case is True:
            value = getattr(value, 'lower', dummy_func)()
            for item in self.iter_column(column):
                if value in getattr(item, 'lower', dummy_func)():
                    return True
            return False
        if explicit is False and ignore_case is False:
            for item in self.iter_column(column):
                if value in item:
                    return True
            return False

    def indices_of_value_by_keyword(self, keyword, **kwargs) -> Iterable:
        """
            Helper function for value_by_keyword returns an iterable object of indices as does all 'indices_of' methods
        """

        explicit, ignore_case, ordered = self._processKwargs('explicit', 'ignore_case', 'ordered',  **kwargs)
        output = ()
        if explicit is True and ignore_case is False:
            output = (index for index in self.__index.get(keyword, ()))
        if explicit is False and ignore_case is False:
            output = (index for key in self.__index if keyword in key for index in self.__index[key])
        if explicit is True and ignore_case is True:
            keyword = getattr(keyword, 'lower', dummy_func)()
            output = (index for key in self.__index if keyword == getattr(key, 'lower', dummy_func)()
                      for index in self.__index[key])
        if explicit is False and ignore_case is True:
            keyword = getattr(keyword, 'lower', dummy_func)()
            output = (index for key in self.__index if keyword in getattr(key, 'lower', dummy_func)()
                      for index in self.__index[key])
        return self._ordered(output, ordered=ordered)

    def value_by_keyword(self, keyword, **kwargs):
        """ Searches the dataset using a single keyword. A simpler version of the search method."""
        return self._convert([self[index]
                              for index in self.indices_of_value_by_keyword(keyword, **kwargs)],
                             convert=self._processKwargs('convert', **kwargs))

    def indices_of_search(self, *args, AND=False, **kwargs) -> Iterable:
        """ Helper function for search returns an iterable object of indices as does all 'indices_of' methods """
        explicit, ignore_case, ordered = self._processKwargs('explicit', 'ignore_case', 'ordered', **kwargs)
        if AND is True:
            sets = [set(self.indices_of_value_by_keyword(keyword,
                                                         explicit=explicit,
                                                         ignore_case=ignore_case,
                                                         ordered=False))
                    for keyword in args]
            return iter(self._ordered(set.intersection(*sets), ordered=ordered))
        else:
            return iter(self._ordered({index for keyword in args
                                       for index in self.indices_of_value_by_keyword(keyword,
                                                                                     explicit=explicit,
                                                                                     ignore_case=ignore_case,
                                                                                     ordered=False)},
                                      ordered=ordered))

    def search(self, *args, AND=False, **kwargs) -> Iterable:
        """ This can take an undefined number of keywords via *args parameter. It searches the dataset using all these
            keywords using its helper method indices_of_search. It takes the indices provided by indices_of_search
            and generates a Table (list of list) data structure and depending on the convert parameter converts it
            into a new IndexedTable.

        :param args: A tuple of keywords, usually text but actually can be of any Hashable type.
        :param AND: (bool: False) By default this is False which implies that the returned dataset will include items
            that have at least 1 keyword noted. True will imply that the dataset returned will only have data that
            includes ALL keywords provided.
        :param explicit: (bool: True) read the Class doc string for more information.
        :param ignore_case: (bool: False) read the Class doc string for more information.
        :param ordered: (bool: True) read the Class doc string for more information.
        :param convert: (bool: True) read the Class doc string for more information.
        :return: Iterable (IndexedTable or List)
        """

        return self._convert([self[index]
                              for index in self.indices_of_search(*args, AND=AND, **kwargs)],
                             convert=self._processKwargs('convert', **kwargs))

    def indices_of_search_by_column(self, column: Hashable, keywords, **kwargs) -> Iterable:
        """
            Helper function for search_by_column returns an iterable object of indices as does all 'indices_of' methods
        """

        explicit, ignore_case, ordered = self._processKwargs('explicit', 'ignore_case', 'ordered', **kwargs)
        columnIter = self.iter_column(column, default=None)
        output = ()
        if columnIter is None:
            return output
        if isinstance(keywords, str):
            keywords = [keywords]
        if ignore_case is True:
            keywords = [getattr(key, 'lower', dummy_func)() for key in keywords]

        if explicit is True and ignore_case is False:
            output = (index for index, value in enumerate(columnIter) if value in keywords)
        if explicit is False and ignore_case is False:
            output = (index for index, value in enumerate(columnIter) for key in keywords if key in value)
        if explicit is True and ignore_case is True:
            output = (index for index, value in enumerate(columnIter)
                      for key in keywords if key == getattr(value, 'lower', dummy_func)())
        if explicit is False and ignore_case is True:
            output = (index for index, value in enumerate(columnIter)
                      for key in keywords if key in getattr(value, 'lower', dummy_func)())
        return self._ordered(output, ordered=ordered)

    def search_by_column(self, column: Hashable, keywords: Union[str, tuple], **kwargs) -> Iterable:
        """ This uses a pair of data. A column which should be value that can be found in the 'columns' KeyedList class
            variable. And 1 or more keywords. The keywords must be a string which is treated like a single value or a
            tuple of values.

        :param column: (Hashable) usually a string which is used iterator over a column using KeyedList's 'iter_column'.
        :param keywords: (str, tuple). Used to compare values found within the output of 'iter_columns'.
        :param explicit: (bool: True) read the Class doc string for more information.
        :param ignore_case: (bool: False) read the Class doc string for more information.
        :param ordered: (bool: True) read the Class doc string for more information.
        :param convert: (bool: True) read the Class doc string for more information.
        :return: Iterable (IndexedTable or List)
        """

        return self._convert([self[index]
                              for index in self.indices_of_search_by_column(column, keywords, **kwargs)],
                             convert=self._processKwargs('convert', **kwargs))

    def indices_of_correlation(self, *args, **kwargs) -> Iterable:
        """ Helper function for correlation returns an iterable object of indices as does all 'indices_of' methods """

        explicit, ignore_case, ordered = self._processKwargs('explicit', 'ignore_case', 'ordered', **kwargs)
        parameters = ('column', 'keywords', 'explicit', 'ignore_case')
        sets = []
        for searchPair in args:
            searchPair = dict(zip(parameters, searchPair))
            if len(searchPair) < 3:
                searchPair.update({'explicit': explicit, 'ignore_case': ignore_case})
            searchPair.update({'ordered': False})
            sets.append(set(self.indices_of_search_by_column(**searchPair)))
        return iter(self._ordered(set.intersection(*sets), ordered=ordered))

    def correlation(self, *args, **kwargs) -> Iterable:
        """ This acts similar to 'search_by_column' in that it looks for pairs as in ('COLUMN_NAME', 'search_value').
            It however, can take multiple such pairs. Each pair is a tuple and the length of the tuple must be either,
            2 or 4. IE: ('USER', 'mongod') or ('USER', 'Mongo', False, True). The last two bool values are the
            arguments 'explicit' and 'ignore_case'. If they are not present, in other words the tuple pair is of size
            2, the 'explicit', and 'ignore_case' parameters provided in the method call are used as defaults. This
            allows for customizing which pairs require explicit/case searching and which don't.

        :param args: (tuple) Tuples of length 2 or 4. IE: ('COLUMN_NAME', 'search_value', True, False) or
            ('COLUMN_NAME', 'search_value')
        :param explicit: (bool: True) read the Class doc string for more information.
        :param ignore_case: (bool: False) read the Class doc string for more information.
        :param ordered: (bool: True) read the Class doc string for more information.
        :param convert: (bool: True) read the Class doc string for more information.
        :return: Iterable (IndexedTable or List)
        """

        return self._convert([self[index]
                              for index in self.indices_of_correlation(*args, **kwargs)],
                             convert=self._processKwargs('convert', **kwargs))

    def incomplete_row_search(self, *args, words_left: float = 0.4, **kwargs) -> Iterable:
        """ This is a special search tool that doesn't have a 'indices_of' paired method. It is meant to run a search
            against a whole line instead of just a single entry. It also is meant to be able to return values even
            when certain words are missing. The goal is to do something similar to a fuzzy match but against a
            whole line. This is a very efficient search as it uses 'has_value' to build out keywords that are then
            passed to 'search' with AND=True set.

        :param args: This is either an undetermined number of keywords or a single item which is a string. If it is a
            single string item this item is stripped and split to build out a list that should loosely represent the row
            in the table that is being searched for.
        :param words_left: The percentage of words required to match. If you send a line: 'Marry had a little lamb' and
            the only word found to exist within the Table is Marry the then the ratio remaining about be 0.2 and thus
            the search would stop and return empty.
        :param explicit: (bool: True) read the Class doc string for more information.
        :param ignore_case: (bool: False) read the Class doc string for more information.
        :param ordered: (bool: True) read the Class doc string for more information.
        :param convert: (bool: True) read the Class doc string for more information.
        :return: Iterable (IndexedTable or List)
        """

        explicit, ignore_case, ordered, convert = self._processKwargs('explicit', 'ignore_case',
                                                                      'ordered', 'convert', **kwargs)

        if len(args) == 1:
            if type(args[0]) is str and len(args[0].strip().split()) > 1:
                args = args[0].strip().split()

        newSearchList = [value for value in args if self.has_value(value, explicit=explicit, ignore_case=ignore_case)]
        if not newSearchList:
            return self._convert([[]], convert=True)

        if len(newSearchList) < 2:
            return self._convert([[]], convert=True)

        if float(len(newSearchList)) / float(len(args)) < words_left:
            return self._convert([[]], convert=True)

        return self.search(*args, AND=True, explicit=explicit, ignore_case=ignore_case,
                           convert=convert, ordered=ordered)

    def fuzzy_has_value(self, value: str, similarity=0.6) -> bool:
        """ Like its 'has_value' cousin however this uses a tool from 'difflib' to do a fuzzy match """
        return len(fmatch(value, self.__index, n=1, cutoff=similarity)) > 0

    def fuzzy_get_values(self, value: str, similarity=0.6) -> list:
        """ Like 'fuzzy_has_value' but instead returns the keywords found if any """
        return fmatch(value, self.__index, n=len(self.__index), cutoff=similarity)

    def fuzzy_has_pair(self, column, value, similarity=0.6) -> bool:
        """ Like its 'has_pair' cousin however this uses a tool from 'difflib' to do a fuzzy match """
        return len(fmatch(value, self.get(column, ()), n=1, cutoff=similarity)) > 0

    def fuzzy_get_pairs(self, column, value, similarity=0.6) -> list:
        """ Like 'fuzzy_has_pair' but instead returns teh keywords found if any """
        return fmatch(value, self.get(column, ()), n=len(self.__index), cutoff=similarity)

    def indices_of_fuzzy_search(self, *args, similarity=0.6, AND=False, **kwargs) -> Iterable:
        """ Helper function for fuzzy_search returns an iterable object of indices as does all 'indices_of' methods """

        ordered = self._processKwargs('ordered', **kwargs)
        number = len(self.__index)
        sets = list((self.__index[match]
                     for keyword in args
                     for match in fmatch(keyword, self.__index, n=number, cutoff=similarity)))
        if AND is True:
            return iter(self._ordered(set.intersection(*sets), ordered=ordered))
        else:
            return iter(self._ordered(set.union(*sets), ordered=ordered))

    def fuzzy_search(self, *args, similarity=0.6, AND=False, **kwargs) -> Iterable:
        """ Like the 'search' method but instead uses tool a from 'difflib' to do a fuzzy match """
        return self._convert([self[index]
                              for index in self.indices_of_fuzzy_search(*args, similarity=similarity,
                                                                        AND=AND, **kwargs)],
                             convert=self._processKwargs('convert', **kwargs))

    def indices_of_fuzzy_column(self, column: str, keywords, similarity=0.6, **kwargs) -> Iterable:
        """ Helper function for fuzzy_column returns an iterable object of indices as does all 'indices_of' methods """
        if isinstance(keywords, str):
            keywords = [keywords]
        length = len(self.__index)
        out = {index
               for keyword in keywords
               for match in set(fmatch(keyword, self.iter_column(column), n=length, cutoff=similarity))
               for index in self.__index[match]}
        return iter(self._ordered(out, ordered=self._processKwargs('ordered', **kwargs)))

    def fuzzy_column(self, column: str, keywords, similarity=0.6, **kwargs) -> Iterable:
        """ Like the 'search_by_column' method but instead uses tool a from 'difflib' to do a fuzzy match """
        return self._convert([self[index]
                              for index in self.indices_of_fuzzy_column(column, keywords,
                                                                        similarity=similarity,
                                                                        **kwargs)],
                             convert=self._processKwargs('convert', **kwargs))

    def indices_of_fuzzy_correlation(self, *args, similarity=0.6, **kwargs):
        """
            Helper function for fuzzy_correlation returns an iterable object of indices as does all 'indices_of' methods
        """

        sets = []
        for searchPair in args:
            if len(searchPair) < 3:
                searchPair = searchPair + (similarity,)
            sets.append(set(self.indices_of_fuzzy_column(*searchPair, ordered=False)))
        return iter(self._ordered(set.intersection(*sets), ordered=self._processKwargs('ordered', **kwargs)))

    def fuzzy_correlation(self, *args, similarity=0.6, **kwargs):
        """ Like the 'correlation' method but instead uses tool a from 'difflib' to do a fuzzy match """
        return self._convert([self[index]
                              for index in self.indices_of_fuzzy_correlation(*args,
                                                                             similarity=similarity,
                                                                             **kwargs)],
                             convert=self._processKwargs('convert', **kwargs))

    def _processKwargs(self, *args, **kwargs):
        if len(args) > 1:
            return [kwargs.get(key, getattr(self, key, None)) for key in args]
        return kwargs.get(args[0], getattr(self, args[0], None))

    def _ordered(self, indices, ordered=True) -> Iterable:
        """ Helper function to order indices when asked or simply return indices unaffected """
        if ordered:
            indices = list(indices)
            indices.sort()
            return indices
        return indices

    def _convert(self, output, convert=True) -> Iterable:
        """ Helper function to convert a new Table (ie: a list of lists) into an IndexedTable if convert is True """
        if convert:
            return IndexedTable(output, columns=self.columns)
        return output

    def _update_index(self, index, obj, remove=False) -> None:
        """ Helper func used by List override methods to update the index dict instead of rebuilding from scratch """
        if remove is True:
            for item in obj:
                self.__index[item].remove(index)
                if not self.__index[item]:
                    del self.__index[item]
        elif isinstance(obj, IndexedTable):
            for key, value in obj.__index.items():
                self.__index[key] = self.__index[key].union(value)
        else:
            for i, items in enumerate(obj, start=index):
                for item in items:
                    self.__index[item].add(i)

    # KeyedTable/List overrides
    def append(self, obj) -> None:
        super(IndexedTable, self).append(obj)
        self._update_index(len(self) - 1, [obj])

    def extend(self, iterable) -> None:
        newList = list(iterable)
        length = len(self)
        super(IndexedTable, self).extend(newList)
        self._update_index(length, newList)

    def insert(self, index, obj) -> None:
        super(IndexedTable, self).insert(index, obj)
        if index == len(self):
            return self._update_index(index, obj)
        self.build_index(rebuild=True)

    def pop(self, index=-1) -> list:
        obj = super(IndexedTable, self).pop(index)
        if index == -1 or index == len(self):
            self._update_index(len(self), obj, remove=True)
            return obj
        self.build_index(rebuild=True)
        return obj

    def clear(self) -> None:
        self.__index.clear()
        super(IndexedTable, self).clear()

    def copy(self, convert=True) -> Union[list, IndexedTable]:
        if convert:
            return IndexedTable(super(IndexedTable, self).copy(), columns=self.columns)
        return super(IndexedTable, self).copy()

    def remove(self, value: list) -> None:
        super(IndexedTable, self).remove(value)
        self.build_index(rebuild=True)

    def reverse(self) -> None:
        super(IndexedTable, self).reverse()
        self.build_index(rebuild=True)

    def sort(self, key=None, reverse=False):
        super(IndexedTable, self).sort(key=key, reverse=reverse)
        self.build_index(rebuild=True)

    def sort_by_column(self, column: Hashable, column_type: Any, reverse: bool = False) -> None:
        super(IndexedTable, self).sort_by_column(column, column_type=column_type, reverse=reverse)
        self.build_index(rebuild=True)


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
        def _helper_get_items(key, item):
            return key, item
        return self.__filter_dict_gen(_helper_get_items)

    def keys(self):
        def _helper_get_items(key, item):
            return key
        return self.__filter_dict_gen(_helper_get_items)

    def values(self):
        def _helper_get_items(key, item):
            return item
        return self.__filter_dict_gen(_helper_get_items)

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
        item = next(self.items())
        del self.__hiddenDict[item[0]]
        return {item[0]: item[1]}

    def setdefault(self, key, default):
        return self.__hiddenDict.setdefault(key, default)

    def update(self, m, **kwargs):
        self.__hiddenDict.update(m, **kwargs)

    def __filter_dict_gen(self, helper_func):
        for key, value in self.__hiddenDict.items():
            if key != '_NamespaceDict__hiddenDict':
                yield helper_func(key, value)
