class GameStart:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_functions = {"p": self.pawn_moves, "R": self.rook_moves, "N": self.knight_moves,
                               "B": self.bishoop_moves, "Q": self.queen_moves, "K": self.king_moves}
        self.moveLog = []
        self.whiteToMove = True
        self.checkmate = False
        self.stalemate = False
        self.empassntantpossible = ()
        self.black_king = (0, 4)
        self.white_king = (7, 4)
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_right_log = [CastleRights(self.current_castling_right.wqs, self.current_castling_right.bqs,
                                              self.current_castling_right.wks, self.current_castling_right.bks)]

    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "bK":
            self.black_king = (move.endRow, move.endCol)
        elif move.pieceMoved == "wK":
            self.white_king = (move.endRow, move.endCol)
        #  pawn promotion move
        if move.ispawnpromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        #  empassant move
        if move.isempassantmove:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.empassntantpossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.empassntantpossible = ()
        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        self.update_castle_rights(move)
        self.castle_right_log.append(CastleRights(self.current_castling_right.wqs, self.current_castling_right.bqs,
                                                  self.current_castling_right.wks, self.current_castling_right.bks))

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch Turns back
            if move.pieceMoved == "bK":
                self.black_king = (move.startRow, move.startCol)
            if move.pieceMoved == "wK":
                self.white_king = (move.startRow, move.startCol)
                # empassant  move
            if move.isempassantmove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.empassntantpossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.empassntantpossible = ()
            # castle Move
            self.castle_right_log.pop()
            self.current_castling_right = self.castle_right_log[-1]

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"

    def valid_moves(self):  # moves considering check
        tempEmpassntantpossible = self.empassntantpossible
        temp_castle_rights = CastleRights(self.current_castling_right.wqs, self.current_castling_right.bqs,
                                          self.current_castling_right.wks, self.current_castling_right.bks,)
        moves = self.all_possible_moves()
        if self.whiteToMove:
            self.castle_moves(self.white_king[0], self.white_king[1], moves)
        else:
            self.castle_moves(self.black_king[0], self.black_king[1], moves)

        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self. whiteToMove = not self.whiteToMove
            if self.in_check():
                moves.remove(moves[i])  # if they attack your king not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undo_move()

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.stalemate = False
            self.checkmate = False
        self.current_castling_right = temp_castle_rights
        self.empassntantpossible = tempEmpassntantpossible
        return moves

    def in_check(self):
        if self.whiteToMove:
            return self.under_attack(self.white_king[0], self.white_king[1])
        else:
            return self.under_attack(self.black_king[0], self.black_king[1])

    def under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opps turn
        ops_moves = self.all_possible_moves()
        self.whiteToMove = not self.whiteToMove  # back to your turn
        for move in ops_moves:
            if move.endRow == r and move.endCol == c:  # under attack
                return True
        return False

    def update_castle_rights(self, move):
        if move.pieceMoved == "wK":
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.pieceMoved == "bK":
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.current_castling_right.wqs = False
                elif move.startCol == 7:
                    self.current_castling_right.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.current_castling_right.bqs = False
                elif move.startCol == 7:
                    self.current_castling_right.bks = False

    def all_possible_moves(self):  # considering without check
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)  # this calls the particular piece type function
        return moves

    def pawn_moves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
        #  kills
            if c-1 >= 0:  # kill to the left
                if self.board[r-1][c-1][0] == "b":  # enemy piece to kill
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.empassntantpossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isempassantmove=True))
            if c+1 <= 7:  # kill to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.empassntantpossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isempassantmove=True))

        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.empassntantpossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isempassantmove=True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r + 1, c + 1) == self.empassntantpossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isempassantmove=True))
        #  add pawn promotion

    def rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    endpiece = self.board[end_row][end_col]
                    if endpiece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif endpiece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def knight_moves(self, r, c, moves):
        knight_directions = ((-2, -1), (-1, -2), (-2, 1), (2, -1), (-1, 2), (1, -2), (1, 2),  (2, 1))
        enemycolor = "w" if self.whiteToMove else "b"
        for km in knight_directions:
            end_row = r + km[0]
            end_col = c + km[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                endpiece = self.board[end_row][end_col]
                if endpiece[0] != enemycolor:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def bishoop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # top left, #topright #bottom left #bottom right
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    endpiece = self.board[end_row][end_col]
                    if endpiece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif endpiece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def queen_moves(self, r, c, moves):
        self.bishoop_moves(r, c, moves)
        self.rook_moves(r, c, moves)

    def king_moves(self, r, c, moves):
        moves_king = ((-1, -1), (1, -1), (-1, 1), (1, 1), (-1, 0),  (0, -1), (0, 1),  (1, 0))
        enecolor = "b" if self.whiteToMove else "w"
        for i in range(8):
            end_row = r + moves_king[i][0]
            end_col = c + moves_king[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                endpiece = self.board[end_row][end_col]
                if endpiece[0] != enecolor:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def castle_moves(self, r, c, moves):
        if self.under_attack(r, c):
            return
        if (self.whiteToMove and self.current_castling_right.wks) or \
                (not self.whiteToMove and self.current_castling_right.bks):
            self.king_side_castle(r, c, moves)
        if (self.whiteToMove and self.current_castling_right.wqs) or \
                (not self.whiteToMove and self.current_castling_right.bqs):
            self.queen_side_castle(r, c, moves)

    def king_side_castle(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.under_attack(r, c+1) and not self.under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def queen_side_castle(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.under_attack(r, c-1) and not self.under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bqs = bqs
        self.bks = bks


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startsq, endsq, board, isempassantmove=False, isCastleMove=False):
        self.startRow = startsq[0]
        self.startCol = startsq[1]
        self.endRow = endsq[0]
        self.endCol = endsq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.ispawnpromotion = (self.pieceMoved == "wp" and self.endRow == 0) or \
                               (self.pieceMoved == "bp" and self.endRow == 7)
        self.isempassantmove = isempassantmove
        if self.isempassantmove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCastleMove = isCastleMove
        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):  # overriding the object
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
