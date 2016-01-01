#!/usr/bin/env python3

class Place:

    _places = { }
    _paths = { }

    def __init__(self,name,path):
        self._name = name
        self._path = path
        Place._places[name] = self
        Place._paths[path] = self

    def place(self):
        return self._name

    def path(self):
        return self._path

    def byName(name):
        return Place._places[name]

    def byPath(path):
        return Place._paths[path]

    def hasName(name):
        return name in Place._places

    def hasPath(path):
        return  path in Place._paths

