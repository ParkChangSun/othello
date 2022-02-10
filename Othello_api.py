from sys import maxsize
import socketio
from sqlalchemy import true
import copy
from collections import deque


class Othello_api:
    sio = socketio.Client()

    def __init__(self, server='http://othello-api.jaram.net/'):
        self.server = server
        self.socket_id = ''
        # 0 : lobby / 1: in game
        self.status = 0
        self.room_list = []
        self.room_info = []
        self.game_info = []

    def setup(self):
        self.call_backs()
        self.sio.connect(self.server)

    def call_backs(self):
        @self.sio.event
        def connect():
            print("I'm connected!")
            self.lobby_loop()

        @self.sio.event
        def connect_error(data):
            print("The connection failed!")

        @self.sio.event
        def disconnect():
            print("I'm disconnected!")

        @self.sio.on('command')
        def handle_command(data):
            # print("command")
            if(data['command'] == 'update_room'):
                self.update_room(data['room_list'])
                return
            elif(data['command'] == 'room_info'):
                self.handle_room_info(data['room_info'], data['game_info'])
                self.status = 1
                return
            elif((data['command'] == 'send_id')):
                self.set_socket_id(data['socket_id'])
                return
            print(data)

        @self.sio.on('*')
        def catch_all(event, data):
            print("event : ", event, " data : ", data)
            pass

    def set_socket_id(self, id):
        self.socket_id = id

    def update_room(self, room_list_server):
        # print("Room List")
        self.room_list = room_list_server

    def handle_room_info(self, room_info, game_info):
        self.room_info = room_info
        self.game_info = game_info
        if(self.game_info['turn'] == self.socket_id):
            self.ai_put_stone()

    def get_socket_id(self):
        self.sio.emit('get_id')

    def get_room(self):
        self.sio.emit('get_room')

    def join_room(self, room_id):
        self.sio.emit("join_room", {'room_id': room_id})

    def ready(self):
        self.sio.emit("ready")

    def create_room(self):
        self.sio.emit("create_room")

    def print_board(self, board):
        for i in range(8):
            for j in range(8):
                print(board[i][j]+1, " ", end='')
            print()
        print()

    def put_stone(self, index):
        print(self.game_info['turn'], self.socket_id)
        if(self.game_info['turn'] == self.socket_id):
            print("put stone!!!!!!!!")
            self.sio.emit("put_stone", {'index': index})

    def game_loop(self):
        while(self.status):
            print("room id ", self.room_info['room_id'])
            if (self.room_info['room_status'] == "waiting"):
                for player_info in self.room_info['player']:
                    if(player_info[1] == 0):
                        print("player ", player_info[0],
                              " is not ready", end='')
                    else:
                        print("player ", player_info[0], " is ready", end='')
                    if(self.socket_id == player_info[0]):
                        print(" (you)")
                    else:
                        print()
                print("command list\nno input: pass(update)\n1 : ready")
                command = input()
                if (len(command.split()) == 0):
                    continue
                elif command.split()[0] == '1':
                    self.ready()
                print()
            elif (self.room_info['room_status'] == "playing"):
                for i in range(2):
                    print(self.game_info['player'][i],
                          "[stone ", i+1, "]", end='')
                    if(self.socket_id == self.game_info['player'][i]):
                        print(" (you)", end='')
                    print(
                        " has ", self.game_info['placeable'][1][i], " stone onboard")
                self.print_board(self.game_info['board'])
                if(self.game_info['turn'] == self.socket_id):
                    print("your turn!!!!\n you can place here")
                    for i in range(len(self.game_info['placeable'][0])):
                        print(i, " :", self.game_info['placeable'][0])
                    print("press index to put")
                command = input()
                if (len(command.split()) == 0):
                    continue
                elif (int(command) < len(self.game_info['placeable'][0])):
                    self.put_stone(int(command))

        self.lobby_loop()
        return

    def lobby_loop(self):
        while(not self.status):
            print("your id : ", self.socket_id, "\nroom list\n", self.room_list,
                  "\ncommand list\nno input: pass(update)\n1 : update room list\n2 : make room\n3 : join room (input \'3 room_index\')")
            command = input()
            if (len(command.split()) == 0):
                continue
            elif command.split()[0] == '1':
                self.get_room()
            elif command.split()[0] == '2':
                self.create_room()
            elif command.split()[0] == '3':
                if (len(command.split()) > 1):
                    self.join_room(
                        self.room_list[int(command.split()[1])]['room_id'])
                else:
                    print("\n\ninput room index!!!!!!!")
            else:
                pass
            print()

        self.game_loop()
        return

    def run(self):
        self.setup()
        self.get_socket_id()

    def ai_put_stone(self):
        # code here!!!!!
        # 방장이 선플레이어
        # 내턴이 안오면 아예 작동을 안하는 듯
        # print(self.game_info)
        # gameinfo
        # if [turn] == socketid 이면 플레이
        # [board] -1 empty 0흑 1백
        # 내보드에서 1흑2백

        # room_id player turn board placeable
        # placeable
        # [0] = placeable spots
        # [1] = stone count
        # [2] = board data that played that placeable spot
        # [3] = current turn player index (board stone number)
        # print(self.socket_id)

        # player에서 앞에 있는 애가 선플레이어(검은색, 내 보드에서는 1)
        # 내보드에서 1흑 2백

        # 일단 player 1일때
        boardPlus1 = copyBoard(self.game_info['board'])
        for i in range(8):
            for j in range(8):
                boardPlus1[i][j] += 1
        othello = OthelloNode(boardPlus1, 4, 1)
        # othello.printBoard()
        # print(terToBoard(int(self.game_info['placeable'][2][0])))

        # if playerNum == 1:
        #     playerNum = 2
        # elif playerNum == 2:
        #     playerNum = 1
        # bestMove = mmOthello(othello, othello.depth, 2)
        bestMove = othello.bestMove()

        print(self.game_info['placeable'][0])
        print(legalPlaySpots(othello.board, 1))
        print(bestMove)
        if legalPlaySpots(othello.board, 1)[bestMove] in self.game_info['placeable'][0]:
            self.put_stone(bestMove)

        self.put_stone(0)

        return


board = []
directions = [[1, 0], [1, 1], [0, 1], [-1, 1],
              [-1, 0], [-1, -1], [0, -1], [1, -1]]


def printBoard(b):
    for i in range(8):
        print(b[i])


def terToBoard(num):
    x = 1144561273430837494885949696427
    res = []
    for i in range(8):
        temp = [-1 for i in range(8)]
        res.append(temp)
    for i in range(8):
        for j in range(8):
            res[i][j] = round(num//x)
            num = num % x
            x = x//3
    # printBoard(res)
    return res


def isValidPos(pos):
    return pos >= 0 and pos < 8


def iterateCells(board, row, col, drow, dcol, handler):
    # start with point+dir
    row = row+drow
    col = col+dcol

    while isValidPos(row) and isValidPos(col):
        icon = board[row][col]
        # empty cell
        if (icon == 0):
            break
        # handler can stop iteration
        if not handler.handleCell(row, col, icon):
            break
        row += drow
        col += dcol


# 어떤 한 점에 둘 수 있는가
def checkLegalPlay(board, row, col, icon):
    enemyIcon = 0
    if icon == 1:
        enemyIcon = 2
    else:
        enemyIcon = 1
    # 모든 방향에 대해서 체크
    for step in directions:
        #  handler is stateful so create new for each direction
        checkCellHandler = CheckCellHandler(enemyIcon)
        iterateCells(board, row, col, step[0], step[1], checkCellHandler)
        if checkCellHandler.isGoodMove():
            return True
    return False


def legalPlaySpots(board, player):
    spots = []
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                if checkLegalPlay(board, i, j, player):
                    spots.append([i, j])
    return spots

# handlecell은 항상 bool반환
# true인 경우는 계속 진행하고 false인 경우는 끝


class CheckCellHandler:
    def __init__(self, enemyIcon):
        self.enemyIcon = enemyIcon
        self.hasOtherPieces = False
        self.endsWithMine = False

    def handleCell(self, row, col, icon):
        if (icon == self.enemyIcon):
            self.hasOtherPieces = True
            return True
        else:
            self.endsWithMine = True
            return False

    def isGoodMove(self):
        return self.hasOtherPieces and self.endsWithMine


class FlipCellHandler:
    def __init__(self, myIcon):
        self.myIcon = myIcon
        self.currentFlipList = []

    # row col은 시작점 아니고 iterate되는 점들(+한칸씩)
    def handleCell(self, board, row, col, icon):
        # 적돌은 리스트에 추가하다가
        if (icon != self.myIcon):
            self.currentFlipList.append([row, col])
            return True
        # 내돌 만났다면 뒤집기
        else:
            for cell in self.currentFlipList:
                board[cell[0]][cell[1]] = self.myIcon
            return False


def iterateCellsFlip(board, row, col, drow, dcol, handler):
    # start with point+dir
    row = row+drow
    col = col+dcol

    while isValidPos(row) and isValidPos(col):
        icon = board[row][col]
        # empty cell
        if (icon == 0):
            break
        # handler can stop iteration
        if not handler.handleCell(board, row, col, icon):
            return len(handler.currentFlipList)
            break
        row += drow
        col += dcol
    return 0


def flip(board, row, col, player):
    count = 0
    if checkLegalPlay(board, row, col, player):
        for step in directions:
            flipCellHandler = FlipCellHandler(player)
            count += iterateCellsFlip(board, row, col,
                                      step[0], step[1], flipCellHandler)
        board[row][col] = player
    return count


class OthelloNode:
    def __init__(self, board, depth, playerNum):
        self.board = board
        self.children = []

        self.depth = depth
        self.playerNum = playerNum
        self.value = self.countStones(playerNum)
        self.createChildren(playerNum)

    def printBoard(self):
        for i in range(8):
            print(self.board[i])
        print('\n')

    def countStones(self, player):
        count = 0
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == player:
                    count += 1
        return count

    def iterateCellsFlip(self, row, col, drow, dcol, handler):
        # start with point+dir
        row = row+drow
        col = col+dcol

        while isValidPos(row) and isValidPos(col):
            icon = self.board[row][col]
            # empty cell
            if (icon == 0):
                break
            # handler can stop iteration
            if not handler.handleCell(self.board, row, col, icon):
                return len(handler.currentFlipList)
                break
            row += drow
            col += dcol
        return 0

    def flip(self, row, col, player):
        count = 0
        if checkLegalPlay(self.board, row, col, player):
            for step in directions:
                flipCellHandler = FlipCellHandler(player)
                count += self.iterateCellsFlip(row, col,
                                               step[0], step[1], flipCellHandler)
            self.board[row][col] = player
        return count

    def createChildren(self, player):
        if self.depth < 0:
            return
        nextNum = 0
        newBoard = copyBoard(self.board)
        for legal in legalPlaySpots(newBoard, player):
            newBoard = copyBoard(self.board)

            flip(newBoard, legal[0], legal[1], self.playerNum)

            if self.playerNum == 1:
                nextNum = 2
            elif self.playerNum == 2:
                nextNum = 1

            node = OthelloNode(newBoard, self.depth-1, nextNum)
            self.children.append(node)

    def bestMove(self):
        bestChoice = 0
        bestValue = 0
        playerNum = 0
        # print("children", len(self.children))
        for i in range(len(self.children)):
            child = self.children[i]

            if self.playerNum == 1:
                playerNum = 2
            elif self.playerNum == 2:
                playerNum = 1
            val = mmOthello(child, child.depth, playerNum)
            if (val > bestValue):
                bestValue = val
                bestChoice = i

        return bestChoice


def copyBoard(board):
    newBoard = []
    for i in board:
        temp = []
        for j in i:
            temp.append(j)
        newBoard.append(temp)
    return newBoard


def mmOthello(node, depth, playerNum):
    if depth == 0:
        return node.value

    bestValue = 0
    for i in range(len(node.children)):
        child = node.children[i]

        # 내보드 1흑 2백
        if playerNum == 1:
            playerNum = 2
        elif playerNum == 2:
            playerNum = 1

        val = mmOthello(child, child.depth, playerNum)
        if (val > bestValue):
            bestValue = val

    return bestValue


# 둘 곳이 없는 경우도 체크?
api = Othello_api()
# board = terToBoard(984971066491994656644)
# print(board)

# board = terToBoard(719211265757284219504227)

# othello = OthelloNode(board)

# othello.createChildren(2)

# print("board default\n")
# othello.children[0].printBoard()
# print("generate 1\n")
# othello.children[0].createChildren(1)

api.run()
