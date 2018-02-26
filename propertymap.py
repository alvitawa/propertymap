
# from data import Data

from collections import OrderedDict
import copy

# TODO: Add mappers after creation of PropertyMap objecct (feature)
# TODO: Return generator of new list instead of existing mapping_head[0], thus preventing possible malfunction

class PropertyMap(object):
    '''
    Data structure with efficient query caching.

    Public Methods:
        obj = PropertyMap(**kwargs): Create a new PropertyMap instance.
        obj.get(**kwargs): Get elements with certain properties.
        obj.update(elements): Add list of elements to the PropertyMap.
        obj.add(element): Add single element to the PropertyMap.

    Example:

        mapping = PropertyMap(
           length_less_than= lambda e, v: len(e) < v,
           elm_isequal= lambda e, v: (e[v[0]] == v[1]) if (len(e) > v[0]) else (False) # check if an element of element has a certain value
        )
                         
        el1 = [0,1,2,3,4]
        el2 = [4,3,99,1,0]
        el3 = [0,1,99,3,4,5,6,7,8]
        mapping.update([el1, el2, el3])

        print((lambda e, v: len(e) < v)(el3, 6))

        print('1: ', mapping.get(length_less_than=3))
        # prints '1: []'

        print('2: ', mapping.get(length_less_than=6))
        # prints '2: [[0,1,2,3,4], [4,3,99,1,0]]' or '2: [[4,3,99,1,0], [0,1,2,3,4]]'

        print('3: ', mapping.get(elm_isequal=(2, 99))) # All elements shorter than 6 where element[2] == 99
        # prints '3: [[4,3,99,1,0], [0,1,99,3,4,5,6,7,8]]' or '3: [[0,1,99,3,4,5,6,7,8], [4,3,99,1,0]]'

        print('4: ', mapping.get(length_less_than=6, elm_isequal=(2, 99))) # All elements shorter than 6 where element[2] == 99
        # prints '4: [[4,3,99,1,0]]'

    '''

    def __init__(self, **kwargs):
        '''
        Return a new PropertyMap instance.

        Passed keyword arguments should be functions that accept 2 arguments and return either True or False,
        these functions are called mappers and represent a query; this is the general format of a mapper:

            def mapper_dummy(element, value):
                return True

        A mapper could be a function that checks wether element[0] has a certain value, so that mapper([4,5], 4)
        returns True. When retrieving elements of the PropertyMap (with get()), you will pass the value and the
        name of the mapper, and the PropertyMap will return all elements where mapper(element, value) is True.

        See the example in the class docstring to understand this mechanic better.
        '''
        self.data = []  # index = element_id
        self.index_tracker = 0
        self.mappers = OrderedDict(kwargs) # OrderedDict([(k, kwargs[k]) for k in sorted(kwargs.keys())])
        # print('Mappers: ', self.mappers)
        def popmap(odict, result):
            try:
                item = odict.popitem(False)
                result[item[0]] = tuple(odict.keys())
                return popmap(odict, result)
            except KeyError:
                return result
        self.mapped_mappers = popmap(copy.deepcopy(self.mappers), {})  # self.mapped_mappers[mapper] returns what mappers come after mapper
        self.main_mapping_head = ([], {prop: {} for prop in self.mappers})  # mapping_head = (all elements that made it to this point, mapping) 
                                                                            # mapping = {property: {value: mapping_head}}

    def __str__(self):
        return ('PropertyMap(' + str(self.data) + ')')

    def str_extra(self):
        '''More detailed string representation.'''
        return ("PropertyMap(\n" + \
                "   Data(%i):\n\n%s\n\n" % (self.index_tracker, str(self.data)) + \
                "   Mappers(%i):\n\n%s\n\n" % (len(self.mappers), str(self.mappers)) + \
                "   Mapped Mappers:\n\n%s\n\n\n" % str(self.mapped_mappers) + \
                "   Main Mapping Head:\n\n%s\n\n" % str_mapping_head(self.data, self.main_mapping_head) +\
                ")\n")

    def get(self, **kwargs):
        '''
        Return all elements with certain properties. To return all elements in the PropertyMap, siply call get() without any arguments.

        Keyword Arguments:
            Key represents a mapper, its value represents the value that will be passed to the mapper as the second argument.

        Example:
            See the example in the class docstring.
        '''
        for kwarg in kwargs:
            if kwarg not in self.mappers:
                raise ValueError('Unknown mapper \'%s\', you have only defined the following: %s' % (str(kwarg), str([k for k in self.mappers.keys()])))
        return self.get_from(self.main_mapping_head, OrderedDict([(prop, kwargs[prop]) for prop in self.mappers if prop in kwargs]))

    def get_from(self, mapping_head, conditions):
        '''
        Not intended for public use, use 'get' instead.

        Get all elements in mapping_head.all where [self.mappers(conditions[k][0])(conditions[k][1]) for k in conditions].count(False) == 0
        '''
        # print('Conditions:', conditions)
        try:
            prop_tuple = conditions.popitem(False) # prop_tuple[0] = property; prop_tuple[1] = property's requested value
            # TODO
        except KeyError:
            prop_tuple = None

        if prop_tuple != None:
            valuemapping = mapping_head[1][prop_tuple[0]]  # mapping_head[1] is the mapping of this mapping_head
            if prop_tuple[1] not in valuemapping:  # Time complexity of (key in D) is apparently O(1), would have to change this if its not.
                valuemapping[prop_tuple[1]] = ([], {prop: {} for prop in self.mapped_mappers[prop_tuple[0]]}) # Make a new mapping head
                for element_id in mapping_head[0]: # mapping_head[0] = all ellements that have been positive for all mappings leading to this point
                    try:
                        mapping_result = self.mappers[prop_tuple[0]](self.data[element_id], prop_tuple[1])
                    except Exception as e:
                        import sys
                        raise type(e)((str(e) + '\n\n(Message from PropertyMap) Exception occured at mapper '
                            'function \'%s\', make shure the function can process all elements that may be added '
                            'to the PropertyMap with any value.') % prop_tuple[0]).with_traceback(sys.exc_info()[2])
                    if mapping_result == True:
                        self.add_to(valuemapping[prop_tuple[1]], element_id)
            return self.get_from(valuemapping[prop_tuple[1]], conditions)  # valuemapping[prop_tuple[1]] = mapping_head.mapping[prop_tuple[0]][prop_tuple[1]]
        else:
            return [self.data[element_id] for element_id in mapping_head[0]]

    def update(self, elements):
        '''
        Add all elements in iterable elements to the PropertyMap.
        '''
        # TODO: Combining PropertyMaps
        for element in elements:
            self.add(element)

    def add(self, element):
        '''
        Add single element to PropertyMap.

        Elements get added to self.data, after which they index gets mapped, so every element added
        will be unique even if two elements have the same value.
        '''
        self.data.append(element)
        self.add_to(self.main_mapping_head, self.index_tracker)
        self.index_tracker += 1

    def add_to(self, mapping_head, element_id):
        '''
        Not intended for public use.

        Add elemend_id to mapping_head.
        '''
        mapping_head[0].append(element_id)
        for prop in mapping_head[1]:
            for value in mapping_head[1][prop]:
                if self.mappers[prop](self.data[element_id], value) == True:
                    self.add_to(mapping_head[1][prop][value], element_id)

def str_mapping_head(data, mapping_head, indenting=''):
    '''Stringify a mapping head.'''
    string = ''
    string += '\n' + indenting + '{'

    string += '\n' + indenting + '\t' + 'Data:'

    str_data = str([data[element_id] for element_id in mapping_head[0]])
    n = 120
    string += ('\n' + indenting + '\t     ').join([str(str_data[i:(i + n)]) for i in range(0, len(str_data), n)])

    string += '\n\n' + indenting + '\t' + 'Mapping: ['

    pvps = [(prop, value) for prop in mapping_head.mapping for value in mapping_head.mapping[prop]]
    string += ('\n' + indenting + '\t\t').join([''] + ['(%s, %s): %s' % (str(prop), str(value), str_mapping_head(data, mapping_head.mapping[prop][value], indenting + '\t\t')) for prop, value in pvps])

    string +=  '\n' + indenting + '\t' + ']'


    string += '\n' + indenting + '}'
    return string


if __name__ == '__main__':
    import unittest
    from tests import *
    unittest.main()
    #  TODO: print usage
