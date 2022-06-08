def prisoner_dilemma(p1, p2):
    if (p1 == 'conf') and (p2 == 'conf'):
        p1_result, p2_result = 5, 5
    elif (p1 == 'conf') and (p2 == 'deny'):
        p1_result, p2_result = 0, 10
    elif (p1 == 'deny') and (p2 == 'conf'):
        p1_result, p2_result = 10, 0
    elif (p1 == 'deny') and (p2 == 'deny'):
        p1_result, p2_result = 1, 1
    return p1_result, p2_result

