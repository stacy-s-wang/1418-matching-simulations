import random
import functools
import numpy as np

def sodaa(students, dorms, verbose = True, clear = False):
    '''
        Runs many to one student optimal DAA on list of strict preferences for Students and Dorms.
        Modifies Dorm().matched and Student(). matched. Assumes that dorms all have already forced 
        preferences.

        Returns dictionary of dorm IDs and corresponding list of matched student IDs sorted by ID.
    '''
    # THIS METHOD IS RIDICULOUSLY SLOW. DO NOT USE.
    if clear:
        for s in students:
            s.matched = None
            s.proposals = 0
        for d in dorms:
            d.matched = []

    unassigned = students.copy()
    round = 0

    while unassigned:
        if verbose: print(f'Round {round}: Unassigned remaining: {len(unassigned)}.')
        round += 1
        unassigned_copy = unassigned.copy()

        for student in unassigned_copy:
            # each student proposes to their proposal number -- in round 1, they propose to position 0 of preflist
            dorm = student.prefs[student.proposals]
            # print(student.id, dorm.id)
            # print(id(dorm.matched))

            # if dorm has nonfull pref list, just assign student to dorm
            if len(dorm.matched) < dorm.quota:
                # match student and dorm
                dorm.matched = dorm.matched + [student]
                student.matched = dorm 

                # update student proposal and remove student from unassigned
                student.proposals += 1 
                unassigned.remove(student)

                dorm.sort_assigned(dorm.matched) # not efficient could be done in O(n) I think oof
            
            # if dorm has full pref list, need to check to see if student is more preferred than current least preferred
            #   assigned to dorm.
            else:
                if dorm.compare(student, dorm.matched[-1]):
                    # add student to end of pref list
                    temp = dorm.matched[-1]
                    dorm.matched = dorm.matched[:-1] + [student]
                    # update unassigned by removing student, adding temp
                    unassigned.remove(student)
                    if temp.proposals < len(dorms): # if temp.proposals = D, then we know it has proposed to all dorms and is assigned to nothing
                        unassigned.append(temp)
                    # update student objects
                    student.matched = dorm
                    student.proposals += 1
                    temp.matched = None

                    dorm.sort_assigned(dorm.matched)
                else:
                    # nothing happens, we just update who student proposed to
                    student.proposals += 1
                    if student.proposals == len(dorms):
                        unassigned.remove(student)   
    return dict([(dorm, list(sorted(dorm.matched, key=lambda x: x.id))) for dorm in dorms])

def mecha(students, dorms, verbose = True, clear = False):
    '''
        Runs many to one student optimal DAA on list of strict preferences for Students and Dorms.
        Modifies Dorm().matched and Student(). matched. Assumes that dorms all have already forced 
        preferences.

        Returns dictionary of dorm IDs and corresponding list of matched student IDs sorted by ID.
    '''
    if clear:
        for s in students:
            s.matched = None
            s.proposals = 0
        for d in dorms:
            d.matched = []
            
    unassigned = students.copy()
    round = 0

    while unassigned:
        if verbose: print(f'Round {round}: Unassigned remaining: {len(unassigned)}.')
        round += 1
        # unassigned_copy = unassigned.copy()

        # each student proposes to their dorm
        for student in unassigned:
            # each student proposes to their proposal number -- in round 1, they propose to position 0 of preflist
            dorm = student.prefs[student.proposals]
            dorm.matched = dorm.matched + [student]
            student.matched = dorm
            student.proposals += 1 
            # unassigned.remove(student)
        # print(len(unassigned))
        unassigned = []
        # dorms now reject or accept
        for dorm in dorms:
            num_matched = len(dorm.matched)
            if num_matched > dorm.quota:
                dorm.sort_assigned(dorm.matched)
                rm_count = 0
                while rm_count < (num_matched - dorm.quota):
                    rejected = dorm.matched[-1]
                    unassigned += [rejected]
                    rejected.matched = None
                    dorm.matched = dorm.matched[:-1]

                    rm_count += 1
    return dict([(dorm, list(sorted(dorm.matched, key=lambda x: x.id))) for dorm in dorms])

def mechb(students, dorms, verbose = True, clear = False):
    '''
        Run student-optimal DAA with strict preferences for Students. Indifferences allowed for Dorms. When 
            indifferences are encountered, we randomly choose one to use.

        Removes indifferences from Dorm.matched so it can be easily printed
    '''
    if clear:
        for s in students:
            s.matched = None
            s.proposals = 0
        for d in dorms:
            d.matched = []
            
    unassigned = students.copy()
    round = 0

    while unassigned:
        if verbose: print(f'Round {round}: Unassigned remaining: {len(unassigned)}.')
        round += 1
        # unassigned_copy = unassigned.copy()

        # each student proposes to their dorm
        for student in unassigned:
            # each student proposes to their proposal number -- in round 1, they propose to position 0 of preflist
            dorm = student.prefs[student.proposals]
            dorm.matched = dorm.matched + [student]
            student.matched = dorm
            student.proposals += 1 
            # unassigned.remove(student)
        unassigned = []
        # dorms now reject or accept
        for dorm in dorms:
            num_matched = sum([len(i) if type(i) is list else 1 for i in dorm.matched])
            if num_matched > dorm.quota:
                dorm.sort_assigned_indiff(dorm.matched)
                rm_count = 0
                while rm_count < (num_matched - dorm.quota):
                    # if is list, this means there are indiffs, so randomize
                    if type(dorm.matched[-1]) is list:
                        # if the entire set of indiff prefs can be removed, do it
                        if len(dorm.matched[-1]) <= (num_matched - dorm.quota - rm_count):
                            # print("all indiffs yoinked")
                            for rejected in dorm.matched[-1]:
                                unassigned += [rejected]
                                rejected.matched = None
                            rm_count += len(dorm.matched[-1])
                            dorm.matched = dorm.matched[:-1]
                        # have to remove some of the students from indifferences: randomize and remove
                        else:
                            # print("break indiffs now!")
                            temp = dorm.matched[-1].copy()
                            random.shuffle(temp)
                            temp_copy = temp.copy()
                            for i in range(0,(num_matched - dorm.quota - rm_count)):
                                rejected = temp_copy[i]
                                unassigned += [rejected]
                                rejected.matched = None
                                temp = temp[1:]
                                rm_count += 1
                            if len(temp) == 1:
                                temp = temp[0]
                            dorm.matched[-1] = temp
                    else:
                        rejected = dorm.matched[-1]
                        unassigned += [rejected]
                        rejected.matched = None
                        dorm.matched = dorm.matched[:-1]

                        rm_count += 1
    # remove indifferences
    for dorm in dorms:
        arr = dorm.matched.copy()
        if not type(arr[0]) is list:
            arr[0] = [arr[0]]
        strict = functools.reduce(lambda a, b: (a + b) if type(b) is list else (a + [b]), arr)
        dorm.matched = strict
    return dict([(dorm, list(sorted(dorm.matched, key=lambda x: x.id))) for dorm in dorms])

def mechc(students, dorms, verbose = True, clear = False):
    '''
        Run student-optimal DAA with strict preferences for Students. Indifferences allowed for Dorms. When 
            indifferences are encountered, we choose students that prefer more, but if there are still ties, we randomize.

        Removes indifferences from Dorm.matched so it can be easily printed
    '''
    if clear:
        for s in students:
            s.matched = None
            s.proposals = 0
        for d in dorms:
            d.matched = []
            
    unassigned = students.copy()
    round = 0

    while unassigned:
        if verbose: print(f'Round {round}: Unassigned remaining: {len(unassigned)}.')
        round += 1
        # unassigned_copy = unassigned.copy()

        # each student proposes to their dorm
        for student in unassigned:
            # each student proposes to their proposal number -- in round 1, they propose to position 0 of preflist
            dorm = student.prefs[student.proposals]
            dorm.matched = dorm.matched + [student]
            student.matched = dorm
            student.proposals += 1 
            # unassigned.remove(student)
        unassigned = []
        # dorms now reject or accept
        for dorm in dorms:
            num_matched = sum([len(i) if type(i) is list else 1 for i in dorm.matched])
            if num_matched > dorm.quota:
                dorm.sort_assigned_indiff(dorm.matched)
                rm_count = 0
                while rm_count < (num_matched - dorm.quota):
                    # if is list, this means there are indiffs, so randomize
                    if type(dorm.matched[-1]) is list:
                        # if the entire set of indiff prefs can be removed, do it
                        if len(dorm.matched[-1]) <= (num_matched - dorm.quota - rm_count):
                            # print("all indiffs yoinked")
                            for rejected in dorm.matched[-1]:
                                unassigned += [rejected]
                                rejected.matched = None
                            rm_count += len(dorm.matched[-1])
                            dorm.matched = dorm.matched[:-1]
                        # have to remove some of the students from indifferences
                        else:
                            # print("break indiffs now!")
                            # temp = dorm.matched[-1].copy()
                            temp = []
                            # choose students who prioritize dorm and remove others. if dorm is ranked the same, then randomize
                            student_ranks = {}
                            for s in dorm.matched[-1]:
                                rank = s.get_dorm_rank(dorm)
                                try:
                                    student_ranks[rank] += [s]
                                except:
                                    student_ranks[rank] = [s]
                            for rank in range(len(s.prefs)):
                                if rank in student_ranks:
                                    random.shuffle(student_ranks[rank])
                                    temp += student_ranks[rank]
                            if len(temp) != len(dorm.matched[-1]): print('clown')
                            temp_copy = temp.copy()
                            for i in range(0,(num_matched - dorm.quota - rm_count)):
                                rejected = temp_copy[len(temp_copy) - 1 - i]
                                unassigned += [rejected]
                                rejected.matched = None
                                temp = temp[:-1]
                                rm_count += 1
                            if len(temp) == 1:
                                temp = temp[0]
                            dorm.matched[-1] = temp
                    else:
                        rejected = dorm.matched[-1]
                        unassigned += [rejected]
                        rejected.matched = None
                        dorm.matched = dorm.matched[:-1]

                        rm_count += 1

    # remove indifferences
    for dorm in dorms:
        arr = dorm.matched.copy()
        if not type(arr[0]) is list:
            arr[0] = [arr[0]]
        strict = functools.reduce(lambda a, b: (a + b) if type(b) is list else (a + [b]), arr)
        dorm.matched = strict
    return dict([(dorm, list(sorted(dorm.matched, key=lambda x: x.id))) for dorm in dorms])

def overall_utility(students):
    '''
        Returns the rankings of each student's match as numpy array
    '''
    ranks = []
    for s in students:
        # self.forced_prefs.index(s1)
        ranks.append(s.prefs.index(s.matched))
    return np.array(ranks)

def linear_swf(rankings, m):
    '''
        Inputs: rankings: np array of ranking of matches students received (indexed at 0)
                m       : number of dorms
        Returns: total social welfare sum(m - x_i + 1) where x_i is ranking indexed at 1
                 array of individual wefares
    '''
    return (np.sum(m - rankings), m - rankings)

def quadratic_swf(rankings, m):
    '''
        Inputs: rankings: list ranking of matches students received (indexed at 0)
                m       : number of dorms
        Returns: (a tuple) total social welfare sum((m - x_i + 1) ^ 2) where x_i is ranking indexed at 1
                 array of individual wefares
    '''
    return (np.sum((m - rankings) ** 2), (m - rankings) ** 2)

def check_stability(students, dorms):
    '''
        Prints out blocking pairs given any matching. By definition, a blocking pair is a student and dorm 
        pairing that prefer each other over their match.

        Returns number of blocking pairs.
    '''
    unstable = 0
    for student in students:
        # find dorms student prefers over current match
        preferred = student.prefs[:student.prefs.index(student.matched)]

        # search for dorm who prefers student over its current match
        for dorm in preferred:
            # sort the dorm's assigned students. starting from the back, compare student to least favored
            #   s of the dorm. dorm prefers student over the identified s
            dorm.sort_assigned(dorm.matched)
            i = -1
            while dorm.compare(student, dorm.matched[i], False) > 0:
                unstable += 1
                print(f'({student.id}, {dorm.id}) is a blocking pair.')
                i -= 1
    return unstable

