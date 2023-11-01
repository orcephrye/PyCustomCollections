from PyCustomCollections.CustomDataStructures import IndexedTable as IT
from collections import defaultdict


index_table = [['One', 'Two', 'Three'], ['Four', 'Five', 'Six'], ['Seven', 'Eight', 'Nine']]
index_table_columns = {'1': 0, '2': 1, '3': 3}


def test_indexedtable_init():
    it = IT(index_table, columns=index_table_columns)
    assert len(it) == 3


def test_indexedtable_str():
    it = IT(index_table, columns=index_table_columns)
    assert str(it) == 'One Two Three\nFour Five Six\nSeven Eight Nine'


def test_indexedtable_build_index():
    it = IT(index_table, columns=index_table_columns)
    it._IndexedTable__index = defaultdict(set)
    it.build_index()
    expected = defaultdict(set,
                           {'One': {0},
                            'Two': {0},
                            'Three': {0},
                            'Four': {1},
                            'Five': {1},
                            'Six': {1},
                            'Seven': {2},
                            'Eight': {2},
                            'Nine': {2}})
    assert it._IndexedTable__index == expected


def test_indexedtable_has_value():
    it = IT(index_table, columns=index_table_columns)
    assert it.has_value('One') is True
    assert it.has_value('one') is False
    assert it.has_value('one', ignore_case=True) is True
    assert it.has_value('One', explicit=True) is True
    assert it.has_value('one', explicit=True) is False
    assert it.has_value('one', explicit=True, ignore_case=True) is True
    assert it.has_value('one', explicit=False) is False
    assert it.has_value('ne', explicit=False) is True
    assert it.has_value('Ne', explicit=False) is False
    assert it.has_value('Ne', explicit=False, ignore_case=True) is True


def test_indexedtable_has_pair():
    it = IT(index_table, columns=index_table_columns)
    assert it.has_pair('1', 'Four') is True
    assert it.has_pair(0, 'Four') is True
    assert it.has_pair('1', 'four', ignore_case=True) is True
    assert it.has_pair('1', 'our', explicit=False) is True
    assert it.has_pair('1', 'ouR', explicit=False) is False
    assert it.has_pair('1', 'ouR', explicit=False, ignore_case=True) is True


def test_indexedtable_indices_of_value_by_keyword():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.indices_of_value_by_keyword('Eight')) == [2]
    assert list(it.indices_of_value_by_keyword('ight', explicit=False)) == [2]
    assert list(it.indices_of_value_by_keyword('ighT', explicit=False, ignore_case=True)) == [2]
    assert list(it.indices_of_value_by_keyword('i', explicit=False)) == [1, 1, 2, 2]
    assert list(it.indices_of_value_by_keyword('i', explicit=False, ordered=False)) == [1, 1, 2, 2]


def test_indexedtable_value_by_keyword():
    it = IT(index_table, columns=index_table_columns)
    assert it.value_by_keyword('Eight') == [['Seven', 'Eight', 'Nine']]
    assert it.value_by_keyword('ight', explicit=False) == [['Seven', 'Eight', 'Nine']]
    assert it.value_by_keyword('i', explicit=False) == [['Four', 'Five', 'Six'],
                                                                ['Four', 'Five', 'Six'],
                                                                ['Seven', 'Eight', 'Nine'],
                                                                ['Seven', 'Eight', 'Nine']]


def test_indexedtable_indices_of_search():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.indices_of_search('Seven')) == [2]
    assert list(it.indices_of_search('One', 'Seven')) == [0, 2]
    assert list(it.indices_of_search('One', 'Seven', AND=True)) == []
    assert list(it.indices_of_search('Four', 'Five', AND=True)) == [1]
    assert list(it.indices_of_search('seven', 'one', ignore_case=True)) == [0, 2]
    assert list(it.indices_of_search('seven', 'one', AND=True, ignore_case=True)) == []
    assert list(it.indices_of_search('four', 'five', AND=True, ignore_case=True)) == [1]
    assert list(it.indices_of_search('ne', explicit=False)) == [0, 2]
    assert list(it.indices_of_search('ne', 'even', explicit=False)) == [0, 2]
    assert list(it.indices_of_search('ne', 'even', AND=True, explicit=False)) == [2]
    assert list(it.indices_of_search('on', 'thr', AND=True, explicit=False, ignore_case=True)) == [0]


def test_indexedtable_search():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.search('Seven')) == [['Seven', 'Eight', 'Nine']]
    assert type(it.search('Seven', convert=True)) is IT
    assert type(it.search('Seven', convert=False)) is list


def test_indexedtable_indices_of_search_by_column():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.indices_of_search_by_column(column='1', keywords='One')) == [0]
    assert list(it.indices_of_search_by_column(column='1', keywords=('One', 'Four', 'Seven'))) == [0, 1, 2]
    assert list(it.indices_of_search_by_column(column=0, keywords=('One', 'Four', 'Seven'))) == [0, 1, 2]
    assert list(it.indices_of_search_by_column(column=0, keywords='one', ignore_case=True)) == [0]
    assert list(it.indices_of_search_by_column(column=0, keywords='one', ignore_case=False)) == []
    assert list(it.indices_of_search_by_column(column=0, keywords='on', explicit=False)) == []
    assert list(it.indices_of_search_by_column(column=0, keywords='On', explicit=False)) == [0]
    assert list(it.indices_of_search_by_column(column=0, keywords='on', explicit=False, ignore_case=True)) == [0]


def test_indexedtable_search_by_column():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.search_by_column(column='1', keywords='One')) == [['One', 'Two', 'Three']]
    assert type(it.search_by_column(column='1', keywords='One', convert=True)) is IT
    assert type(it.search_by_column(column='1', keywords='One', convert=False)) is list


def test_indexedtable_indices_of_correlation():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.indices_of_correlation(('1', 'One'))) == [0]
    assert list(it.indices_of_correlation(('1', 'One'), ('2', 'Two'))) == [0]
    assert list(it.indices_of_correlation(('1', 'Four'))) == [1]
    assert list(it.indices_of_correlation(('1', 'One'), ('1', 'Four'))) == []
    assert list(it.indices_of_correlation(('1', 'One'), ('2', 'two'))) == []
    assert list(it.indices_of_correlation(('1', 'One'), ('2', 'two', False, True))) == [0]
    assert list(it.indices_of_correlation(('1', 'One'), ('2', 'wo', False, False))) == [0]
    assert list(it.indices_of_correlation(('1', 'One'), ('2', 'Wo', False, True))) == [0]


def test_indexedtable_correlation():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.correlation(('1', 'One'))) == [['One', 'Two', 'Three']]
    assert type(it.correlation(('1', 'One'))) is IT
    assert type(it.correlation(('1', 'One'), convert=False)) is list


def test_indexedtable_incomplete_row_search():
    it = IT(index_table, columns=index_table_columns)
    assert it.incomplete_row_search('One', 'Two') == [['One', 'Two', 'Three']]
    assert it.incomplete_row_search('One') == [[]]
    assert it.incomplete_row_search('one', 'two', ignore_case=True) == [['One', 'Two', 'Three']]
    assert it.incomplete_row_search('ne', 'wo', explicit=False) == [['One', 'Two', 'Three']]


def test_indexedtable_fuzzy_has_value():
    it = IT(index_table, columns=index_table_columns)
    assert it.fuzzy_has_value('One') is True
    assert it.fuzzy_has_value('one') is True
    assert it.fuzzy_has_value('ne') is True
    assert it.fuzzy_has_value('On') is True
    assert it.fuzzy_has_value('on') is False
    assert it.fuzzy_has_value('n') is False
    assert it.fuzzy_has_value('on', similarity=0.4) is True


def test_indexedtable_fuzzy_get_values():
    it = IT(index_table, columns=index_table_columns)
    assert it.fuzzy_get_values('One') == ['One']
    assert it.fuzzy_get_values('ne') == ['One', 'Nine']
    assert it.fuzzy_get_values('ve') == ['Five']
    assert it.fuzzy_get_values('ve', similarity=0.5) == ['Five', 'Seven']


def test_indexedtable_fuzzy_has_pair():
    it = IT(index_table, columns=index_table_columns)
    assert it.fuzzy_has_pair('1', 'Four') is True
    assert it.fuzzy_has_pair(0, 'Four') is True
    assert it.fuzzy_has_pair('1', 'four') is True
    assert it.fuzzy_has_pair('1', 'our') is True
    assert it.fuzzy_has_pair('1', 'ouR') is False
    assert it.fuzzy_has_pair('1', 'ouR', similarity=0.5) is True


def test_indexedtable_fuzzy_get_pairs():
    it = IT(index_table, columns=index_table_columns)
    assert it.fuzzy_get_pairs('1', 'Four') == ['Four']
    assert it.fuzzy_get_pairs(0, 'Four') == ['Four']
    assert it.fuzzy_get_pairs('1', 'four') == ['Four']
    assert it.fuzzy_get_pairs('1', 'our') == ['Four']
    assert it.fuzzy_get_pairs('1', 'ouR') == []
    assert it.fuzzy_get_pairs('1', 'ouR', similarity=0.5) == ['Four']


def test_indexedtable_indices_of_fuzzy_search():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.indices_of_fuzzy_search('Seven')) == [2]
    assert list(it.indices_of_fuzzy_search('One', 'Seven')) == [0, 2]
    assert list(it.indices_of_fuzzy_search('One', 'Seven', AND=True)) == []
    assert list(it.indices_of_fuzzy_search('Four', 'Five')) == [1]
    assert list(it.indices_of_fuzzy_search('seven', 'one')) == [0, 2]
    assert list(it.indices_of_fuzzy_search('seven', 'one', AND=True)) == []
    assert list(it.indices_of_fuzzy_search('four', 'five', AND=True)) == [1]
    assert list(it.indices_of_fuzzy_search('ne')) == [0, 2]
    assert list(it.indices_of_fuzzy_search('ne', 'even')) == [0, 2]
    assert list(it.indices_of_fuzzy_search('ne', 'even', similarity=0.5, AND=True)) == [2]
    assert list(it.indices_of_fuzzy_search('on', 'thr', similarity=0.4, AND=True)) == [0]


def test_indexedtable_fuzzy_search():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.fuzzy_search('Seven')) == [['Seven', 'Eight', 'Nine']]
    assert type(it.fuzzy_search('Seven', convert=True)) is IT
    assert type(it.fuzzy_search('Seven', convert=False)) is list


def test_indexedtable_indices_of_fuzzy_column():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.indices_of_fuzzy_column(column='1', keywords='One')) == [0]
    assert list(it.indices_of_fuzzy_column(column='1', keywords=('One', 'Four', 'Seven'))) == [0, 1, 2]
    assert list(it.indices_of_fuzzy_column(column=0, keywords=('One', 'Four', 'Seven'))) == [0, 1, 2]
    assert list(it.indices_of_fuzzy_column(column=0, keywords='one')) == [0]
    assert list(it.indices_of_fuzzy_column(column=0, keywords='on')) == []
    assert list(it.indices_of_fuzzy_column(column=0, keywords='On')) == [0]
    assert list(it.indices_of_fuzzy_column(column=0, keywords='on', similarity=0.4)) == [0]


def test_indexedtable_fuzzy_column():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.fuzzy_column(column='1', keywords='One')) == [['One', 'Two', 'Three']]
    assert type(it.fuzzy_column(column='1', keywords='One', convert=True)) is IT
    assert type(it.fuzzy_column(column='1', keywords='One', convert=False)) is list


def test_indexedtable_indices_of_fuzzy_correlation():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.indices_of_fuzzy_correlation(('1', 'One'))) == [0]
    assert list(it.indices_of_fuzzy_correlation(('1', 'One'), ('2', 'Two'))) == [0]
    assert list(it.indices_of_fuzzy_correlation(('1', 'Four'))) == [1]
    assert list(it.indices_of_fuzzy_correlation(('2', 'Two', 0.4))) == [0]
    assert list(it.indices_of_fuzzy_correlation(('1', 'One'), ('1', 'Four'))) == []
    assert list(it.indices_of_fuzzy_correlation(('1', 'One'), ('2', 'two', 0.4))) == [0]
    assert list(it.indices_of_fuzzy_correlation(('1', 'one'), ('2', 'wo'), similarity=0.4)) == [0]
    assert list(it.indices_of_fuzzy_correlation(('1', 'One'), ('2', 'Wo'))) == []


def test_indexedtable_fuzzy_correlation():
    it = IT(index_table, columns=index_table_columns)
    assert list(it.correlation(('1', 'One'))) == [['One', 'Two', 'Three']]
    assert type(it.correlation(('1', 'One'))) is IT
    assert type(it.correlation(('1', 'One'), convert=False)) is list
