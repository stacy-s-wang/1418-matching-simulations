import numpy as np
import math
import random
import functools

class Dorm(object):
    def __init__(self, id = 0, prefs = [], forced_prefs = [], quota = 0, matched = []):
        self.id = id
        self.prefs = prefs
        self.forced_prefs = forced_prefs
        self.pref_indices = {}
        self.quota = quota
        self.matched = matched

    def set_preferences(self, prefs):
        self.prefs = prefs
        return prefs

    def set_quota(self, quota):
        self.quota = quota
        return quota

    def set_forced_preferences(self, prefs):
        self.forced_prefs = prefs
        return prefs

    def draw_preferences(self, students, indiff_score = 0.8):
        '''
            Takes in list of Student objects and induces random preferences with possible indifferences
        
            indiff_score: percent of indifferences (number of separate groups) -- the higher, the lower the indiffs
            prefs       : lists of lists representing induced prefs. tuples represent indifference i.e. [1, 3, (6,7), 5, 4].
        ''' 
        prefs = []
        students = students.copy()

        random.shuffle(students)
        n = len(students)

        indices = random.sample(list(range(0, n)), k = math.floor(n * indiff_score))
        indices.sort()
        if indices[-1] != n:
            indices.append(n)
        if indices[0] != 0:
            indices.insert(0,0)

        for i in range(len(indices)-1):
            if indices[i+1] - indices[i] == 1:
                prefs.append(students[indices[i]])
            else:
                prefs.append(students[indices[i]:indices[i+1]])

        self.prefs = prefs
        return prefs

    def draw_quota(self, num_students, num_dorms):
        '''
            Sets quota to be some variation of at least num_students/num_dorms
        '''
        # 20% of the time, we set the quota below the number allowed
        if random.random() < 0.2:
            self.quota = math.ceil((random.random() * -0.5 + 1) * num_students / num_dorms)
        else:
            self.quota = math.ceil((random.random() * 0.5 + 1) * num_students / num_dorms)
        
        return self.quota

    def force_preferences(self):
        '''
            Force a random set of preferences onto 
        '''
        forced_prefs = []
        for s in self.prefs:
            if type(s) is list:
                s = s.copy()
                random.shuffle(s)
                for i in s:
                    forced_prefs.append(i)
            else:
                forced_prefs.append(s)
        
        self.forced_prefs = forced_prefs
        return self.forced_prefs
        
    def compare(self, s1, s2, use_forced = True):
        '''
            Compares s1 and s2 on self's forced preference list OR on preference list.
        
            Returns: If using forced prefs, returns True if s1 is preferred over s2, False otherwise.
                     If using actual prefs, returns 1 if s1 is preferred over s2, 0 if indifferent, -1 otherwise.
        '''
        if (not self.prefs) or (not self.forced_prefs):
            print("prefs:", self.prefs, "forced:", self.forced_prefs)
            return None
        if use_forced:
            try:
                return True if self.forced_prefs.index(s1) < self.forced_prefs.index(s2) else False
            except Exception as e:
                print(e)
                print(s1, s2)
                raise(e)
        else:
            if s1 is s2:
                return 0

            # now use non forced prefs
            s1_index = s2_index = -1

            # we check hash table of pref_indices to see if s1, s2 are in it
            if s1_index in self.pref_indices:
                s1_index = self.pref_indices[s1.id]
            if s2_index in self.pref_indices:
                s2_index = self.pref_indices[s2.id]

            for i in range(0,len(self.prefs)):
                if s1_index != -1 and s2_index != -1:
                    break

                if type(self.prefs[i]) == list:
                    for s in self.prefs[i]:
                        if s1_index < 0 and s.id == s1.id:
                            s1_index = i
                            self.pref_indices[s1.id] = i
                        if s2_index < 0 and s.id == s2.id:
                            s2_index = i
                            self.pref_indices[s2.id] = i
                else:
                    if s1_index < 0 and self.prefs[i].id == s1.id:
                        s1_index = i
                        self.pref_indices[s1.id] = i
                    if s2_index < 0 and self.prefs[i].id == s2.id:
                        s2_index = i
                        self.pref_indices[s2.id] = i

            if s1_index < s2_index: return 1
            if s1_index == s2_index: return 0
            if s1_index > s2_index: return -1

    def sort_assigned(self, arr):
        # true story: this is mergesort (credits to geek2geek because i can't be bothered)
        if len(arr) > 1:
            mid = len(arr)//2
            L = arr[:mid]
            R = arr[mid:]
    
            # Sorting the first half
            self.sort_assigned(L)
    
            # Sorting the second half
            self.sort_assigned(R)
    
            i = j = k = 0
            while i < len(L) and j < len(R):
                if self.compare(L[i], R[j]):
                    arr[k] = L[i]
                    i += 1
                else:
                    arr[k] = R[j]
                    j += 1
                k += 1

            while i < len(L):
                arr[k] = L[i]
                i += 1
                k += 1
  
            while j < len(R):
                arr[k] = R[j]
                j += 1
                k += 1

    def make_indiff(self, arr):
        '''
            Helper function for sort_assigned_indiff
            Take an arr of strict preferences and re-adds the indifferences and sets that to self.matched
        '''
        output = [arr[0]]
        j = 0
        for i in range(1, len(arr)):
            # print(i, output)
            if not type(output[j]) is list:
                if self.compare(arr[i], output[j], False) != 0:
                    j += 1
                    output += [arr[i]]
                    # print(output)
                elif self.compare(arr[i], output[j], False) == 0:
                    output[j] = [output[j]] + [arr[i]]
            else:
                if self.compare(arr[i], output[j][0], False) != 0:
                    j += 1
                    # print(output)
                    output += [arr[i]]
                elif self.compare(arr[i], output[j][0], False) == 0:
                    output[j] = output[j] + [arr[i]]
        self.matched = output
        return output

    def sort_assigned_indiff(self, arr):
        '''
            Takes in list (possibly with indifferences included) and sorts it.
            Modifies self.matched in place (includes indifferences)

            Returns: self.matched (includes indifferences)
        '''
        arr = arr.copy()
        if not type(arr[0]) is list:
            arr[0] = [arr[0]]
        strict = functools.reduce(lambda a, b: (a + b) if type(b) is list else (a + [b]), arr)
        # print("should be reg list: ", str([i.id for i in strict]))
        # try:
        #     print("should be reg list: ", str([i.id for i in strict]))
        # except:
        #     print("should be reg list: ", str([i for i in strict]))
        self.sort_assigned(strict)
        self.make_indiff(strict)
        return self.matched

class Student(object):
    def __init__(self, id = 0, prefs = []):
        self.id = id
        self.prefs = prefs
        self.matched = None
        self.proposals = 0

    def set_preferences(self, prefs):
        self.prefs = prefs
        return prefs

    def draw_preferences(self, dorms):
        self.prefs = random.sample(dorms, len(dorms))
        return self.prefs

    def get_dorm_rank(self, dorm):
        return self.prefs.index(dorm)

    def compare(self, d1, d2):
        '''
            Compares d1 and d2 on self's preference list.
        
            Returns: True if d1 is preferred over d2, False otherwise.
        '''
        return True if self.prefs.index(d1) < self.prefs.index(d2) else False
