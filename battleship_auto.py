#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 01:02:07 2018

@author: mathpn
"""
from random import randint, choice
from os import system
import numpy as np
from matplotlib import pyplot as plt
from copy import deepcopy as dc
from math import sqrt

def Battleship():
    size = 10
    level = 1

    def create_ships(board, ships):
        for ship in range(0, len(ships)):
            valid = False
            while not valid:
                x = randint(1, 10 - ships[ship])-1
                y = randint(1, 10 - ships[ship])-1
                o = randint(0, 1)
                if o == 0:
                    ori = "v"
                else:
                    ori = "h"
                valid = validate(board,ships[ship],x,y,ori)
            board = place_ship(board,ships[ship],ori,x,y)
        return board

    def place_ship(board, ship, ori, x, y):
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
        elif ori == "h" and y+ship > 10:
            return False
        else:
            if ori == "v":
                for i in range(0, ship):
                    if board[x+i][y] != 0:
                        return False
            elif ori == "h":
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
        else:
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

    def probability_mixed(board, hit, count, ships, size):
        prob = probability_attack(board, hit, ships, size)
        prob2 = probability_hunt(board, ships, size, hit)
        count = 0
        if len(hit) > 1 and hit[-2][0] == hit[-1][0] and sum(prob[hit[-1][0], :]) == 0:
            count = 1
        elif len(hit) > 1 and hit[-2][1] == hit[-1][1] and sum(prob[:, hit[-1][ 1]]) == 0:
            count = 1
        if len(hit) > 1 and hit[-2][0] == hit[-1][0]:
            prob[hit[-1][0], :] = np.prod([prob[hit[-1][0], :], 3])
        elif len(hit) > 1 and hit[-2][1] == hit[-1][1]:
            prob[:, hit[-1][1]] = np.prod([prob[:, hit[-1][1]], 3])
        if np.amax(prob) > 0:
            prob = np.divide(prob, np.amax(prob))
        prob = prob * (1 - (1/2) * count)
        prob2 = prob2 * (1/2) * count
        prob3 = np.add(prob, prob2)
        return prob3

    def computer(level, status, count, ships):
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
        elif level == 1:
            if status == 1 and miss <= 3:
                prob = probability_mixed(board, hit, count, ships, size)
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
        for i in range(size):
            for j in range(size):
                if board[i][j] != 0:
                    return False
        return True

    board = []
    board_ships = []
    board2_ships = []
    board2 = []

    for x in range(size):
        board.append(["O"] * size)

    for x in range(size):
        board_ships.append([0] * size)

    for x in range(size):
        board2.append(["O"] * size)

    for x in range(size):
        board2_ships.append([0] * size)

    ships = [5, 4, 3, 3, 2]

    ships_human = create_ships(board_ships, ships)

    points_comp = False

    turn = 0
    status = 0
    miss = 0
    hit = []
    count = 0
    comp_guess = []
    points_comp = 0
    while not points_comp:

        if len(hit) > 2 and ((hit[-1][0] != hit[-2][0] and hit[-2][0] == hit[-3][0])\
        or hit[-1][1] != hit[-2][1] and hit[-2][1] == hit[-3][1]):
            count = 0

        comp_guess = computer(level, status, count, ships)

        if comp_guess[-1]:
            status = 0
            hit = []
            miss = 0
            count = 0

        guess_row2 = comp_guess[0]
        guess_col2 = comp_guess[1]
        complete = False

        if ships_human[guess_row2][guess_col2] == 1:
            board[guess_row2][guess_col2] = 'B'
            ships_human[guess_row2][guess_col2] = 0
            hit.append([guess_row2, guess_col2])
            status = 1
            miss = 0
            complete = True
        if not complete:
            board[guess_row2][guess_col2] = "X"
            miss += 1
        #input('Press enter to exit...')
        points_comp = check_points(ships_human, size)
        turn += 1

    return turn
