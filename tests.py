
import unittest
import warnings
import time
import random

from propertymap import PropertyMap

class Tests(unittest.TestCase):

    def usage_example(self):
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


    def test_simple(self):
        mapping = PropertyMap(
                                length_less_than= lambda e, v: len(e) < v,
                                length_is= lambda e, v: len(e) == v,
                                length_greater_than= lambda e, v: len(e) > v,
                                ev0isv1= lambda e, v: (e[v[0]] == v[1]) if (len(e) > v[0]) else (False) # check if an element of element has a certain value
                             )
        el1 = [0,1,2,3,4]
        mapping.add([0,1,2,3,4])
        self.assertEqual(mapping.get(length_less_than=10), [el1])
        self.assertEqual(mapping.get(length_less_than=3), [])

        el2 = [4,3]
        mapping.add(el2)
        self.assertEqual(mapping.get(length_is=2), [el2])

        self.assertEqual(mapping.get(length_is=5, ev0isv1=(2,11)), [])
        el3 = [5,5,11,5,5]
        mapping.add(el3)
        # print(mapping)
        self.assertEqual(mapping.get(length_is=5, ev0isv1=(2,11)), [el3])
        # print(mapping)
        self.assertEqual(mapping.get(ev0isv1=(2,11), length_is=5), [el3])

        # print(mapping)

    def test_performance(self):
        control = []
        exponential = (4 if (random.randint(1,6) != 1) else 6)
        for i in range(10**exponential):
            control.append(list(str(i * 2 / 3)))
        subject = PropertyMap(has_elm= lambda e, v: v in e)
        subject.update(control)

        selm = '4'

        control_times = []
        subject_times = []

        itrs = random.randint(0,40)
        for i in range(itrs):

            control_start = time.time()
            control_results = []
            for elm in control:
                if selm in elm:
                    control_results.append(elm)
            control_end = time.time()

            subject_start = time.time()
            subject_results = subject.get(has_elm=selm)
            subject_end = time.time()

            self.assertEqual(control_results, subject_results)

            print('Test %i' % i)

            control_time = control_end - control_start
            print('Control: %fs' % control_time)
            control_times.append(control_time)

            subject_time = subject_end - subject_start
            print('Subject: %fs' % subject_time)
            subject_times.append(subject_time)



        avg_control = (sum(control_times) / len(control_times))
        print('Average of Control: ', avg_control)
        avg_subject = (sum(subject_times) / len(subject_times))
        print('Average of Subject: ', avg_subject)

        if avg_control < avg_subject:
            warnings.warn(('\nInefficient time while doing %i iterations of exponential %i. '+ \
                          ' Control: %fs Subject: %fs') % (itrs, exponential, avg_control, avg_subject))


if __name__ == '__main__':
    unittest.main()