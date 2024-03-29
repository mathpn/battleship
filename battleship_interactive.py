#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 01:02:07 2018

@github: mathpn

Name: Matheus Pedroni

## THIS CODE IS LICENSED UNDER THE GPL-3.0 LICENSE ##
## https://www.gnu.org/licenses/gpl-3.0.en.html ##
"""
from copy import deepcopy as dc
from math import sqrt
from random import randint, choice
from os import system
from typing import List

import numpy as np


def print_board(board):
    row_spacement = ' ' if len(board) <= 10 else '  '
    print(
        f"   {row_spacement.join([str(i + 1) for i in range(10)])}"
        f" {' '.join([str(i + 1) for i in range(10, len(board))])}"
    )
    for i, row in enumerate(board):
        spacement = '  ' if (i + 1) < 10 else ' '
        print(f"{i + 1}{spacement}{row_spacement.join(row)}")


def create_ships(board, ship_sizes: List[int]):
    for size in ship_sizes:
        # genereate random coordinates and validate the postion
        valid = False
        while not valid:
            x = randint(1, 10 - size)-1
            y = randint(1, 10 - size)-1
            o = randint(0, 1)
            if o == 0:
                ori = "v"
            else:
                ori = "h"
            valid = validate(board,size,x,y,ori)
        board = place_ship(board,size,ori,x,y)
    return board


def place_ship(board, ship, ori, x, y):
    # place ship based on orientation
    if ori == "v":
        for i in range(0, ship):
            board[x+i][y] = 1
    elif ori == "h":
        for i in range(ship):
            board[x][y+i] = 1
    return board


def validate(board, ship, x, y, ori):
    if ori == "v" and x+ship > 10:
        return False
    if ori == "h" and y+ship > 10:
        return False
    if ori == "v":
        for i in range(0, ship):
            if board[x+i][y] != 0:
                return False
    if ori == "h":
        for i in range(0, ship):
            if board[x][y+i] != 0:
                return False
    return True


def probability_hunt(board, ships, size, hit):
    prob = np.zeros((size, size))
    for ship in ships:
        verify = []
        verify.append(['O'] * ship)
        for row in range(0, len(board[0])):
            for k in range(0, len(board[0]) - ship + 1):
                if 'X' not in board[row][k:k + ship]:
                    prob[row, k:k + ship] += 1
        for col in range(0, len(board[0])):
            column = []
            for row in range(0, len(board[0])):
                column.append(board[row][col])
            for j in range(0, len(board[0]) - ship + 1):
                if 'X' not in column[j:j + ship]:
                    prob[j:j + ship, col] += 1
    prob = np.divide(prob, np.amax(prob))
    for i in hit:
        prob[i[0], i[1]] = 0.1
    for row in range(0, len(board[0])):
        for i in range(0, len(board[0])):
            if board[row][i] == 'B':
                prob[row, i] = 0
    return prob


def distance(hit, i):
    if hit.index(i) == (len(hit) - 1):
        dist = 0.1
        return dist
    horizontal = i[0] - hit[hit.index(i) + 1][0]
    vertical = i[1] - hit[hit.index(i) + 1][1]
    dist = sqrt(horizontal ** 2 + vertical ** 2)
    return dist


def probability_attack(board, hit, ships, size):
    prob = np.zeros((size, size))
    for ship in ships:
        for row in range(0, len(board[0])):
            for i in hit:
                if i[0] == row:
                    for k in range(i[1] - ship + 1, i[1] + 1):
                        if k >= 0:
                            if 'X' not in board[row][k:k + ship]:
                                if (k + ship) < len(board[0]):
                                    prob[row, k:k + ship] += (1 - 0.1 * (1.5 * distance(hit, i) - hit.index(i)))
        for col in range(0, len(board[0])):
            column = []
            for i in hit:
                if i[1] == col:
                    for k in range(i[0] - ship + 1, i[0] + 1):
                        if k >= 0:
                            for row in range(0, len(board[0])):
                                column.append(board[row][col])
                            if 'X' not in column[k:k + ship]:
                                if (k + ship) < len(board[0]):
                                    prob[k:k + ship, col] += (1 - 0.1 * (1.5 * distance(hit, i) - hit.index(i)))
    for i in hit:
        prob[i[0], i[1]] = 0
    for row in range(0, len(board[0])):
        for i in range(0, len(board[0])):
            if board[row][i] == 'B':
                prob[row, i] = 0
    return prob



def probability_mixed(board, hit, ships, size):
    prob = probability_attack(board, hit, ships, size)
    prob2 = probability_hunt(board, ships, size, hit)
    count = 0
    if len(hit) > 1 and hit[-2][0] == hit[-1][0] and sum(prob[hit[-1][0], :]) == 0:
        count = 1
    elif len(hit) > 1 and hit[-2][1] == hit[-1][1] and sum(prob[:, hit[-1][ 1]]) == 0:
        count = 1
    elif len(hit) > 2 and ((hit[-1][0] != hit[-2][0] and hit[-2][0] == hit[-3][0])\
    or hit[-1][1] != hit[-2][1] and hit[-2][1] == hit[-3][1]):
        count = 1
    elif len(hit) > 1 and hit[-2][0] == hit[-1][0]:
        prob[hit[-1][0], :] = np.prod([prob[hit[-1][0], :], 3])
    elif len(hit) > 1 and hit[-2][1] == hit[-1][1]:
        prob[:, hit[-1][1]] = np.prod([prob[:, hit[-1][1]], 3])
    elif np.amax(prob) > 0:
        prob = np.divide(prob, np.amax(prob))
    prob = prob * (1 - (1/2) * count)
    prob2 = prob2 * (1/2) * count
    prob3 = np.add(prob, prob2)
    return prob3


def computer(board, size, hit, miss, level, status, ships):
    guess_row = []
    guess_col = []
    change = False
    if level == 0:
        guess_row = choice(range(0, size))
        guess_col = choice(range(0, size))
        while board[guess_row][guess_col] != 'O':
            guess_row = choice(range(0, size))
            guess_col = choice(range(0, size))
        return [guess_row, guess_col]

    if status == 1 and miss <= 3:
        prob = probability_mixed(board, hit, ships, size)
    elif status == 1 and miss > 3:
        change = True
        prob = probability_hunt(board, ships, size, hit)
    else:
        prob = probability_hunt(board, ships, size, hit)
    maximum = np.argwhere(prob == np.amax(prob))
    if np.amax(prob) != 0:
        index = choice(range(0, maximum.shape[0]))
        guess_row = maximum[index, 0]
        guess_col = maximum[index, 1]
    else:
        guess_row = choice(range(0, size))
        guess_col = choice(range(0, size))
        while board[guess_row][guess_col] != 'O':
            guess_row = choice(range(0, size))
            guess_col = choice(range(0, size))
    #plt.imshow(prob, interpolation = 'nearest')
    #plt.show()
    return [guess_row, guess_col, change]


def check_points(board, size):
    #simple for loop to check all cells in 2d board
    #if any cell contains a char that is not a hit or a miss return false
    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                return False
    return True



def main():
    size = input("What will be the size of the board? \n We strongly suggest 10x10 \n Bear in mind that larger sizes games are harder and longer! \n Insert here: ")

    def isint(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    while not isint(size):
        size = input('Oops, that\'s not a valid input, it should be an integer number: ')
    size = int(size)

    level = input('The game can be played in easy or hard modes. \n Type 1 for easy or 2 for hard: ')
    while not isint(level):
        size = input('Oops, that\'s not a valid input, it should be 1 or 2: ')
    while int(level) not in range(0, 3):
        level = input('Oops, that\'s not a valid input, it should be 1 or 2: ')
    level = int(level) - 1

    while  not isint(size) or size < 10:
        size = input('Oops! The size should be at least 10!')

    board = []
    board_ships = []
    board2_ships = []
    board2 = []

    for _ in range(size):
        board.append(["O"] * size)

    for _ in range(size):
        board_ships.append([0] * size)

    for _ in range(size):
        board2.append(["O"] * size)

    for _ in range(size):
        board2_ships.append([0] * size)

    ship_sizes = [5, 4, 3, 3, 2]

    ships_human = create_ships(board_ships, ship_sizes)
    ships_comp = create_ships(board2_ships, ship_sizes)

    system('cls||clear')
    print('There are 5 Battleships in each board. \n One of size 5x1, other of size 2x1, two of size 3x1 and the last of size 2x1 \n Your goal is to sink your oponent\'s ships before he sinks yours!')
    print('On each board, failed attacks will be marked as X \n And succesful ones with B (from Battlefield)')
    input('Press enter to continue...')
    system('cls||clear')
    print('Hello, I\'m The Computer and I\'m much more intelligent than you, human! \n Let\'s play. \n I\'ll let you begin!')
    input('Press enter to continue...')
    system('cls||clear')
    turn = 1
    status = 0
    miss = 0
    hit = []
    comp_guess = []
    points_human = 0
    points_comp = 0
    while turn > 0:
        system('cls||clear')
        print('Turn', turn)
        print('Your vision of computer\'s board:')
        print_board(board2)

        valid = False
        while not valid:
            guess_row = input("Guess Row: ")
            while not isint(guess_row):
                guess_row = input('It should be an integer: ')
            guess_row = int(guess_row) - 1
            guess_col = input("Guess Col: ")
            while not isint(guess_col):
                guess_col = input('It should be an integer: ')
            guess_col = int(guess_col) - 1
            complete = False

            if (guess_row < 0 or guess_row > (size - 1)) or (guess_col < 0 or guess_col > (size - 1)):
                print("Oops, that's not even in the ocean.")
            elif board2[guess_row][guess_col] != 'O':
                print("You guessed that one already.")
            else:
                 valid = True
            input('Press enter to continue...')

        if ships_comp[guess_row][guess_col] == 1:
            print("How could you, human? You hit one of my battleships!")
            board2[guess_row][guess_col] = "B"
            ships_comp[guess_row][guess_col] = 0
            print_board(board2)
            input('Press enter to continue...')
        else:
            print("You missed my battleships, idiot!")
            board2[guess_row][guess_col] = "X"
            print_board(board2)
            input('Press enter to continue...')
                    
        print('The Computer vision of your board:')
        print_board(board)

        comp_guess = computer(board, size, hit, miss, level, status, ship_sizes)

        if comp_guess[-1]:
            status = 0
            hit = []
            miss = 0

        guess_row2 = comp_guess[0]
        guess_col2 = comp_guess[1]
        complete = False

        if ships_human[guess_row2][guess_col2] == 1:
            print("Aha! I hit one of your Battleships!")
            board[guess_row2][guess_col2] = 'B'
            ships_human[guess_row2][guess_col2] = 0
            hit.append([guess_row2, guess_col2])
            print_board(board)
            status = 1
            miss = 0
            complete = True
        if not complete:
            print("The Computer missed your Battleships. Simply bad luck.")
            board[guess_row2][guess_col2] = "X"
            print_board(board)
            miss += 1
        points_human = check_points(ships_comp, size)
        points_comp = check_points(ships_human, size)
        if points_comp and not points_human:
            system('cls||clear')
            print('HAHAHAHAHA *laughs robotically* I won! I knew I would!')
            input('Press enter to continue...')
            input('Press enter to exit...')
            break
        elif not points_comp and points_human:
            system('cls||clear')
            print('Congratulations, human, you won by pure luck!')
            input('Press enter to continue...')
            input('Press enter to exit...')
            break
        elif points_comp and points_human:
            system('cls||clear')
            print('It\'s a tie!')
            input('Press enter to continue...')
            input('Press enter to exit...')
            break
        else:
            input('Press enter to continue...')

        turn += 1


if __name__ == '__main__':
    main()
