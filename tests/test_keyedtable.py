import pytest
from PyCustomCollections.CustomDataStructures import KeyedTable
from collections.abc import Iterable


def test_keyedtable_init():
    kt = KeyedTable([['1', '2'], ['3', '4']])
    assert len(kt) == 2
    assert str(kt) == "[['1', '2'], ['3', '4']]"


def test_keyedtable_init_columns():
    kt = KeyedTable([['1', '2'], ['3', '4']], columns={'One': 1, 'Two': 2})
    assert len(kt) == 2
    assert str(kt) == "[['1', '2'], ['3', '4']]"
    assert kt.columns == {'One': 1, 'Two': 2}


def test_keyedtable_getitem():
    kt = KeyedTable([['1', '2'], ['3', '4']], columns={'One': 0, 'Two': 1})
    assert kt[0] == ['1', '2']  # Get Row
    assert kt['One'] == ['1', '3']  # Get Column


def test_keyedtable_get():
    kt = KeyedTable([['1', '2'], ['3', '4']], columns={'One': 0, 'Two': 1})
    assert kt.get('One') == ['1', '3']
    assert kt.get('Cheese') is None
    assert kt.get('Cheese', default='Test') == 'Test'


def test_keyedtable_get_cell():
    kt = KeyedTable([['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']], columns={'One': 0, 'Two': 1, 'Three': 3})
    assert kt.get_cell(1, 1) == '5'
    assert kt.get_cell(2, 2) == '9'
    assert kt.get_cell(0, 'One') == '1'
    assert kt.get_cell(10, 1) is None
    assert kt.get_cell(1, 'Cheese') is None
    assert kt.get_cell(1, 'Cheese', default='Test') == 'Test'


def test_keyedtable_iter_column():
    kt = KeyedTable([['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']], columns={'One': 0, 'Two': 1, 'Three': 3})
    kt_iter = kt.iter_column(0)
    assert isinstance(kt_iter, Iterable) is True
    assert list(kt_iter) == ['1', '4', '7']
    kt_iter = kt.iter_column('Two')
    assert isinstance(kt_iter, Iterable) is True
    assert list(kt_iter) == ['2', '5', '8']
    kt_iter = kt.iter_column('Test')
    assert kt_iter is None
    kt_iter = kt.iter_column('Test', default='Test')
    assert kt_iter == 'Test'


def test_keyedtable_iter_row():
    kt = KeyedTable([['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']], columns={'One': 0, 'Two': 1, 'Three': 3})
    kt_iter = kt.iter_row(0)
    assert isinstance(kt_iter, Iterable) is True
    assert list(kt_iter) == ['1', '2', '3']
    kt_iter = kt.iter_row(10)
    assert kt_iter is None
    kt_iter = kt.iter_row(10, default='Test')
    assert kt_iter == 'Test'


def test_keytable_sort_by_column():
    kt = KeyedTable([['4', '5', '6'], ['7', '8', '9'], ['1', '2', '3']], columns={'One': 0, 'Two': 1, 'Three': 3})
    kt.sort_by_column(0, str, reverse=False)
    assert kt[0] == ['1', '2', '3']
    kt = KeyedTable([['4', '5', '6'], ['7', '8', '9'], ['1', '2', '3']], columns={'One': 0, 'Two': 1, 'Three': 3})
    kt.sort_by_column('One', str, reverse=False)
    assert kt[0] == ['1', '2', '3']
    kt = KeyedTable([['4', '5', '6'], ['7', '8', '9'], ['1', '2', '3']], columns={'One': 0, 'Two': 1, 'Three': 3})
    kt.sort_by_column('One', str, reverse=True)
    assert kt[0] == ['7', '8', '9']
