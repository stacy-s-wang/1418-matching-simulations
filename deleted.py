def mechb(students, dorms, verbose = True, clear = False):
    '''
        Run student-optimal DAA with strict preferences for Students. Indifferences allowed for Dorms. When 
            indifferences are encountered, we randomly choose one to use.
    '''
    if clear:
        for s in students:
            s.matched = None
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

            # if dorm has nonfull pref list, just assign student to dorm
            if len(dorm.matched) < dorm.quota:
                # match student and dorm
                dorm.matched = dorm.matched + [student]
                student.matched = dorm 

                # update student proposal and remove student from unassigned
                student.proposals += 1 
                unassigned.remove(student)

                dorm.sort_assigned_indiff(dorm.matched) # not efficient could be done in O(n) I think oof
            
            # if dorm has full pref list, need to check to see if student is more preferred than current least preferred
            #   assigned to dorm.
            else:
                if dorm.matched[-1] is list:
                    # compared dorm is going to be in a list
                    if dorm.compare(student, dorm.matched[-1][0]):
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
                    
                    pass
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

def better_sodaa(students, dorms, verbose = True, clear = False):
    '''
        Run student-optimal DAA with strict preferences for Students. Indifferences allowed for Dorms. When 
            indifferences are encountered, we randomly choose one to use.
    '''
    if clear:
        for s in students:
            s.matched = None
        for d in dorms:
            d.matched = []
            
    unassigned = students.copy()
    round = 0

    while unassigned:
        if verbose: print(f'Round {round}: Unassigned remaining: {len(unassigned)}.')
        round += 1
        unassigned_copy = unassigned.copy()

        # each student proposes to their dorm
        for student in unassigned_copy:
            # each student proposes to their proposal number -- in round 1, they propose to position 0 of preflist
            dorm = student.prefs[student.proposals]
            dorm.matched = dorm.matched + [student]
            #  print(dorm.id, dorm.matched)
            student.matched = dorm
            student.proposals += 1 
            unassigned.remove(student)

        # print("students all proposed:", unassigned)
        # dorms now reject or accept
        for dorm in dorms:
            # num matched = sum([len(i) if type(i) is list else 1 for i in test])
            # print(dorm.matched)
            num_matched = sum([len(i) if type(i) is list else 1 for i in dorm.matched])
            #  print(num_matched)
            if num_matched > dorm.quota:
                dorm.sort_assigned(dorm.matched)
                rm_count = 0
                while rm_count < (num_matched - dorm.quota):
                    rejected = dorm.matched[-1]
                    unassigned += [rejected]
                    rejected.matched = None
                    dorm.matched = dorm.matched[:-1]

                    rm_count += 1
        
        # print("dorms all rejected:", unassigned)
        
    return dict([(dorm, list(sorted(dorm.matched, key=lambda x: x.id))) for dorm in dorms])