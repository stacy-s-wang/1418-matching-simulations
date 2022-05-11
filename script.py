from objects import Dorm, Student
from functions import check_stability, overall_utility, mecha, mechb, mechc, linear_swf, quadratic_swf
import math
import random
import numpy as np
# import matplotlib.pyplot as plt

S = 1500
D = 10
# random.seed(20220508)
for indiff in [0.2, 0.5, 0.8]:
    indiff_mat = np.empty(shape=(500, 49))
    matching_ranks = np.empty(shape=(3*S, 500))
    indrow = 0
    for config in range(5):
        print(f"############ CONFIG {config} INDIFF {indiff} ############", flush=True)
        # draw students and dorms
        students = [Student(id = 's' + str(i)) for i in range(1,S+1)]
        dorms = [Dorm(id = 'd' + str(i)) for i in range(1,D+1)]

        for d in dorms:
            d.set_quota(math.ceil(S/D)) # we want every school to be the same -- don't vary
            d.draw_preferences(students, indiff_score=indiff)

        for s in students:
            s.draw_preferences(dorms)

        # now force dorm preferences 500 times
        for iter in range(500):
            if iter % 50 == 0:
                print(f"Iteration {iter} just started.", flush=True)
            
            row = np.empty(49)
            row[0] = config

            for d in dorms:
                d.force_preferences()

            matching = mecha(students, dorms, verbose=False, clear=True)
            rankings = overall_utility(students)
            linsw, lin = linear_swf(rankings,D)
            row[1] = linsw
            row[2:7] = np.percentile(lin, [0, 25, 50, 75, 100])
            row[7] = np.mean(lin)
            row[8] = np.std(lin)
            quadsw, quad = quadratic_swf(rankings,D)
            row[9] = quadsw
            row[10:15] = np.percentile(quad, [0, 25, 50, 75, 100])
            row[15] = np.mean(quad)
            row[16] = np.std(quad)

            matching_ranks[0:S,iter] = rankings

            if indrow % 500 == 0:
                blocking = check_stability(students, dorms)
                if blocking != 0:
                    print(f"Something is wrong here, mechanism A has {blocking} pairs in row {indrow}.", flush=True)

            matching = mechb(students, dorms, verbose=False, clear=True)
            rankings = overall_utility(students)
            linsw, lin = linear_swf(rankings,D)
            row[17] = linsw
            row[18:23] = np.percentile(lin, [0, 25, 50, 75, 100])
            row[23] = np.mean(lin)
            row[24] = np.std(lin)
            quadsw, quad = quadratic_swf(rankings,D)
            row[25] = quadsw
            row[26:31] = np.percentile(quad, [0, 25, 50, 75, 100])
            row[31] = np.mean(quad)
            row[32] = np.std(quad)

            matching_ranks[S:2*S,iter] = rankings

            if indrow % 500 == 0:
                blocking = check_stability(students, dorms)
                if blocking != 0:
                    print(f"Something is wrong here, mechanism B has {blocking} pairs in row {indrow}.", flush=True)

            matching = mechc(students, dorms, verbose=False, clear=True)
            rankings = overall_utility(students)
            linsw, lin = linear_swf(rankings,D)
            row[33] = linsw
            row[34:39] = np.percentile(lin, [0, 25, 50, 75, 100])
            row[39] = np.mean(lin)
            row[40] = np.std(lin)
            quadsw, quad = quadratic_swf(rankings,D)
            row[41] = quadsw
            row[42:47] = np.percentile(quad, [0, 25, 50, 75, 100])
            row[47] = np.mean(quad)
            row[48] = np.std(quad)

            matching_ranks[2*S:3*S,iter] = rankings

            if indrow % 500 == 0:
                blocking = check_stability(students, dorms)
                if blocking != 0:
                    print(f"Something is wrong here, mechanism C has {blocking} pairs in row {indrow}.", flush=True)

            indiff_mat[indrow] = row
            indrow += 1
        np.savetxt(f"trial_simulation_indiff_{indiff}_config_{config}.csv", indiff_mat[config*500:(config+1)*500], delimiter=",", fmt="%10.8f")
    # np.savetxt(f"simulation_indiff_{indiff}.csv", indiff_mat, delimiter=",", fmt="%10.8f")
    np.savetxt(f"rankings_{indiff}.csv", matching_ranks, delimiter=",", fmt="%d")
    print(f"******************Saved simulation_indiff_{indiff}.csv!******************\n\n", flush=True)