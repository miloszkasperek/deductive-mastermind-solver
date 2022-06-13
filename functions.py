import random
import itertools
import copy


def phi_g(guess, g1):
    """Creates a list of literals in the form: ['code[index_of_a_pin]', '=', 'guess[index_of_a_pin]'
    which correspond to the pieces of information about the code from a guess
    and one of the possible interpretations of the 'green' (pins which are of good color and in good place) part
    of a feedback from this guess"""
    phi_g_literals = []
    for i in list(g1):
        phi_g_literals.append([f"code[{i}]", "=", guess[i]])
    for j in list(set(range(len(guess))) - g1):
        phi_g_literals.append([f"code[{j}]", "≠", guess[j]])
    return phi_g_literals


def phi_o(guess, g1, o1):
    """Creates a list of literals in the form: ['code[index_of_a_pin]', '=', 'guess[index_of_a_pin]'
    or ['code[index_of_a_pin]', '=', 'guess[index_of_a_pin] which correspond
    to the pieces of information about the code from a guess
    and one of the possible interpretations
    of the 'orange' (pins which are of one of the code colors but in bad place) part
    of a feedback from this guess"""
    phi_o_literals = []
    for n in list(o1):
        for m in list(set(range(len(guess))) - g1):
            if n != m:
                phi_o_literals.append([[f"code[{m}]", "=", guess[n]]])
    if len(phi_o_literals) == 0:
        phi_o_literals.append([])
    return phi_o_literals


def phi_r(guess, g1, o1):
    """Creates a list of literals in the form: ['code[index_of_a_pin]', '=', 'guess[index_of_a_pin]'
        or ['code[index_of_a_pin]', '=', 'guess[index_of_a_pin] which correspond
        to the pieces of information about the code from a guess
        and one of the possible interpretations
        of the 'red' (pins which are not of the code colors) part
        of a feedback from this guess"""
    phi_r_literals = []
    for z in list(set(range(len(guess))) - (g1 | o1)):
        for x in list(set(range(len(guess))) - g1):
            if z != x:
                phi_r_literals.append([f"code[{x}]", "≠", guess[z]])
    return phi_r_literals


def create_bt_alternatives(guess, feedback):
    """Creates a list of alternative lists of literals which correspond
        to the pieces of information about the code from a guess
        and one of the possible interpretations of the feedback"""
    bt_alternatives = []
    bold_g1 = tuple(itertools.combinations(range(len(guess)), len(feedback[0])))
    for g1 in bold_g1:
        pg = phi_g(guess, set(g1))
        bold_o1 = tuple(itertools.combinations(tuple(set(range(len(guess)))-set(g1)), len(feedback[1])))
        for o1 in bold_o1:
            po = phi_o(guess, set(g1), set(o1))
            pr = phi_r(guess, set(g1), set(o1))
            for k in range(len(po)):
                bt_alternatives.append(pg + po[k] + pr)
    return bt_alternatives


def bt_remove_duplicates(bt):
    """Deletes duplicates from every alternative list of literals of a given bt"""
    for alternative in bt:
        for i, literal1 in enumerate(alternative):
            for j, literal2 in enumerate(alternative):
                if literal2 == literal1 and i != j:
                    alternative.remove(literal2)


def create_bt_alternatives_from_all_turns_combined(every_turn_bt_alternatives, number_of_colors):
    """Creates a list of alternative lists of literals which correspond
        to the pieces of information about the code from all guesses
        and one of the possible interpretations of their feedbacks"""
    bt_alternatives_from_all_turns_combined = [[]]
    for i, turn in enumerate(every_turn_bt_alternatives):
        if len(turn) > 1:
            bt_alternatives_from_all_turns_combined_copy = copy.deepcopy(bt_alternatives_from_all_turns_combined)
            counter_2 = 0
            for j, alt in enumerate(bt_alternatives_from_all_turns_combined_copy):
                counter_1 = 0
                for k in range(len(turn) - 1):
                    alt2 = copy.deepcopy(alt)
                    bt_alternatives_from_all_turns_combined.insert(j + k + 1 + counter_2, alt2)
                    counter_1 += 1
                counter_2 += counter_1
            iterator = []
            for c in range(int(len(bt_alternatives_from_all_turns_combined)/len(turn))):
                for r in turn:
                    iterator.append(r)

            for n, k in enumerate(iterator):
                for m in k:
                    bt_alternatives_from_all_turns_combined[n].append(m)
        else:
            for alternative in bt_alternatives_from_all_turns_combined:
                for b in turn[0]:
                    alternative.append(b)
        if i > 0:
            bt_alternatives_from_all_turns_combined = alts_sifting(bt_alternatives_from_all_turns_combined, number_of_colors)

    return bt_alternatives_from_all_turns_combined


def alts_sifting(bt_alternatives_from_all_turns_combined, number_of_colors):
    """Deletes all contradictory alternatives from a given list of alternatives and returns changed list"""
    alts_copy = copy.deepcopy(bt_alternatives_from_all_turns_combined)
    to_del = []
    for r, alt in enumerate(alts_copy):
        for literal in copy.deepcopy(alt):
            x = [[literal[0], "=", c] for c in list(set(range(number_of_colors)) - {literal[2]})]
            y = [[literal[0], "≠", d] for d in range(number_of_colors)]
            if literal[1] == "=":
                if [literal[0], "≠", literal[2]] in alt:
                    to_del.append(r)
                    break
                elif any(ele in alt for ele in x):
                    to_del.append(r)
                    break
            elif literal[1] == "≠":
                if [literal[0], "=", literal[2]] in alt:
                    to_del.append(r)
                    break
            elif all(elem in literal for elem in y):
                to_del.append(r)
                break

    for index in sorted(to_del, reverse=True):
        del bt_alternatives_from_all_turns_combined[index]

    return bt_alternatives_from_all_turns_combined


def determine_possibilities(possible_answers, alts, guesses2):
    """Determines a set of possible answers considering bt alternatives"""
    possibilities_list = [[] for _ in alts]
    possible_answers = set(possible_answers)
    for i, a in enumerate(alts):
        to_remove = set()
        for form in a:
            if form[1] == '=':
                for pos in list(possible_answers):
                    if pos[int(form[0][-2])] != form[2]:
                        to_remove.add(pos)
            elif form[1] == '≠':
                for pos in list(possible_answers):
                    if pos[int(form[0][-2])] == form[2]:
                        to_remove.add(pos)
        possibilities_list[i] = possible_answers - to_remove - guesses2

    return possibilities_list


def generate_code(possible_guesses):
    """Given a set of possible codes - chooses a code for the game (randomly)"""
    code = random.sample(possible_guesses, 1)[0]
    return code


def generate_feedback(guess, code):
    """Given a guess and a code, generates feedback to the guess"""
    g2 = {o for o in range(len(guess)) if guess[o] == code[o]}
    o2 = set()
    for p in list(set(range(len(guess))) - g2):
        for u in list(set(range(len(guess))) - g2):
            if u != p and guess[u] == code[p]:
                o2.add(u)
    r = {y for y in list(set(range(len(guess))) - g2 - o2)}
    feedback = tuple([tuple(["g" for _ in g2]), tuple(["o" for _ in o2]), tuple(["r" for _ in r])])
    return feedback


def run_game(number_of_pins: int, number_of_colors: int, number_of_turns: int):
    """Runs the whole solver"""
    possible_guesses = tuple(itertools.product([color for color in range(number_of_colors)], repeat=number_of_pins))
    turns = 0
    guesses = ()
    guesses2 = set()
    code = generate_code(possible_guesses)
    print("CODE: ", code)
    every_turn_bt_alternatives = []
    game_over = False
    lens = []

    while turns != number_of_turns:
        turns += 1
        guess = generate_code(possible_guesses)
        feedback = generate_feedback(guess, code)
        print(f"TURN {turns}:", "GUESS: ", guess, "FEEDBACK: ", feedback)
        bt = create_bt_alternatives(guess, feedback)
        bt_remove_duplicates(bt)
        lens.append(len(bt))
        every_turn_bt_alternatives.append(bt)
        guesses = guesses + (guess, feedback)
        guesses2.add(guess)

        if len(feedback[0]) == number_of_pins:
            print("You've guessed it in: : ", turns, " turns.")
            print('Your guesses: ', guesses)
            game_over = True
            break
    if game_over is False:
        bt_alternatives_from_all_turns_combined = create_bt_alternatives_from_all_turns_combined(every_turn_bt_alternatives, number_of_colors)
        bt_alternatives_from_all_turns_combined = alts_sifting(bt_alternatives_from_all_turns_combined, number_of_colors)
        posses = determine_possibilities(possible_guesses, bt_alternatives_from_all_turns_combined, guesses2)
        posses = set().union(*posses)
        print("CODE: ", code)
        print(f"POSSIBLE ANSWERS AFTER {number_of_turns} TURNS: ", posses)
    else:
        run_game(number_of_pins, number_of_colors, number_of_turns)
