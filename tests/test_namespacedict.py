import pytest
from PyCustomCollections.CustomDataStructures import NamespaceDict


def test_namespacedict_init():
    nd = NamespaceDict(this='', that='')
    assert hasattr(nd, 'this') is True
    assert hasattr(nd, 'that') is True


def test_namespacedict_clean():
    nd = NamespaceDict(this='', that='')
    assert hasattr(nd, 'this') is True
    assert hasattr(nd, 'that') is True
    nd.clear()
    assert hasattr(nd, 'this') is False
    assert hasattr(nd, 'that') is False


def test_namespacedict_copy():
    nd = NamespaceDict(this='', that='')
    expect = {'this': '', 'that': ''}
    assert nd.copy() == expect


def test_namespacedict_fromkeys():
    nd = NamespaceDict()
    expect = {'this': None, 'that': None}
    assert nd.fromkeys(['this', 'that']) == expect


def test_namespacedict_get():
    nd = NamespaceDict(this='hi', that='world')
    assert nd.this == 'hi'


def test_namespacedict_items():
    nd = NamespaceDict(this='hi', that='world')
    assert next(nd.items()) == ('this', 'hi')


def test_namespacedict_keys():
    nd = NamespaceDict(this='hi', that='world')
    assert next(nd.keys()) == 'this'


def test_namespacedict_pop():
    nd = NamespaceDict(this='hi', that='world')
    assert nd.pop('that') == 'world'


def test_namespacedict_popitem():
    nd = NamespaceDict(this='hi', that='world')
    assert nd.popitem() == {'this': 'hi'}
    assert hasattr(nd, 'this') is False


def test_namespacedict_setdefault():
    nd = NamespaceDict(this='hi', that='world')
    assert getattr(nd, 'this', None) == 'hi'
    nd.setdefault('this', 'cheese')
    assert getattr(nd, 'this', None) != 'cheese'
    assert getattr(nd, 'this', None) == 'hi'


def test_namespacedict_update():
    nd = NamespaceDict(this='hi', that='world')
    nd.update({'this': 'bye', 'cheese': 'balls'})
    assert getattr(nd, 'this', None) == 'bye'
    assert getattr(nd, 'cheese', None) == 'balls'

