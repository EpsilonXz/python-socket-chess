class GameState():
    def __init__(self):
        #  The board is an 8x8 2d list, each element of the list has 2 chars
        #  The first char is the color of the piece
        #  The second char is the type of the piece
        #  "--" Represents an empty space with no pieces on it
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],

        ]
        #print(self.board.reverse())
        self.moveFunctions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                              'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.whiteToMove = True
        self.moveLog = []
        self.ready = False
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () #  Coordinates for the square where enpassant capture is available
        self.currentCastelingRight = CastleRights(True, True, True, True)
        self.castleRightsLog =  [CastleRights(self.currentCastelingRight.wks, self.currentCastelingRight.bks,
                                              self.currentCastelingRight.wqs, self.currentCastelingRight.bqs)]
        
    

    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #  log the move
        self.whiteToMove = not self.whiteToMove #  Switch turns
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        
        #  Pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        #  Enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #  Capturing the pawn
        
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #  Only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        #  Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #  Kingside Castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #  Moves the rook
                self.board[move.endRow][move.endCol+1] = '--' #  Erase old rook
            else: #  Queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # Moves the rook
                self.board[move.endRow][move.endCol+2] = '--' #  Erase the old rook

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastelingRight.wks, self.currentCastelingRight.bks,
                                                 self.currentCastelingRight.wqs, self.currentCastelingRight.bqs))
    
    
    def undo_move(self):
        if len(self.moveLog) != 0: #  Make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #  Switch turns
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            #  Undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #  Leave landing sqaure blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #  Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            
            #  Undo casteling rights
            self.castleRightsLog.pop() #  Get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastelingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            #  Undo catle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #  Kingside
                    self.board(move.endRow)[move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #  Queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
    

    '''Update the castle rights given the move'''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastelingRight.wks = False
            self.currentCastelingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastelingRight.bks = False
            self.currentCastelingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #  Left rook
                    self.currentCastelingRight.wqs = False
                elif move.startCol == 7: #  Right rook
                    self.currentCastelingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #  Left rook
                    self.currentCastelingRight.bqs = False
                elif move.startCol == 7: #  Right rook
                    self.currentCastelingRight.bks = False
                


    def get_valid_moves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastelingRight.wks, self.currentCastelingRight.bks,
                                        self.currentCastelingRight.wqs, self.currentCastelingRight.bqs) #  Copy the current casteling rights
        moves = self.get_possible_moves() #  Generate all possible moves
        '''
        if self.whiteToMove:
            self.get_castle_moves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.get_castle_moves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        '''
        for i in range(len(moves) - 1, -1, -1): #  When removing from a list go backwards through the list
            self.make_move(moves[i])

            self.whiteToMove = not self.whiteToMove #  Make move switches the turns so we switch it back so <in_check> will work
            if self.in_check():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undo_move()

        if len(moves) == 0: #  Either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        if self.whiteToMove:
            self.get_castle_moves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.get_castle_moves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastelingRight = tempCastleRights

        return moves

    ''' Check if player is in check '''
    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.square_under_attack(self.blackKingLocation[0], self.blackKingLocation[1])

    
    ''' Check if the enemy can attack the sqaure '''
    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove #  Switch to opponent's turn
        oppMoves = self.get_possible_moves() 
        self.whiteToMove = not self.whiteToMove #  Switch turns back
        for move in oppMoves: #  Generate all of the opponents moves
            if move.endRow == r and move.endCol == c: #  Square is under attack
                return True
        
        return False    


    def get_possible_moves(self):
        moves = []
        for r in range(len(self.board)): #  Number of rows
            for c in range(len(self.board[r])): #  Number of collons in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #  Calls the move function
        return moves



    '''Get all possible moves for the pawn located at row, col and add those moves to the list'''
    def get_pawn_moves(self, r, c, moves):
        if self.whiteToMove: #  Focus on white's pawn moves
            if self.board[r-1][c] == "--": #  1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #  2 pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: #  Captures to the left
                if self.board[r-1][c-1][0] == 'b': #  Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: #  Captures to the right
                if self.board[r-1][c+1][0] == 'b': #  Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
                        

        else: #  Focus on black's pawn moves
            if self.board[r+1][c] == "--": #  1 pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": # 2 pawn advance
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0: #  Captures to the left
                if self.board[r+1][c-1][0] == 'w': #  Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7: #  Captures to the right
                if self.board[r+1][c+1][0] == 'w': #  Check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))
        
        #  ''' Add pawn promotions ''' #


    
    '''Get all possible moves for the rook located at row, col and add those moves to the list'''
    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #  Empty space is valid
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #  Enemy piece is valid
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                        break
                    else: #  Friendly piece is invalid
                        break
                else: #  Location off board is invalid
                    break


    '''Get all possible moves for the knight located at row, col and add those moves to the list'''
    def get_knight_moves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #  Not an ally piece (Either empty or enemy piece)
                    moves.append(Move((r,c), (endRow, endCol), self.board))

    
    '''Get all possible moves for the bishop located at row, col and add those moves to the list'''
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #  Empty space is valid
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #  Enemy piece is valid
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                        break
                    else: #  Friendly piece is invalid
                        break
                else: #  Location off board is invalid
                    break

    '''Get all possible moves for the queen located at row, col and add those moves to the list'''
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    
    '''Get all possible moves for the king located at row, col and add those moves to the list'''
    def get_king_moves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1,1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: 
                    moves.append(Move((r, c), (endRow, endCol), self.board))
        #self.get_castle_moves(r, c, moves, allyColor)


    '''Generate all valid castle moves for the king at (r, c) and add them to the list of moves '''
    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return #  Can't castle while we are in check (Thats a rule in chess)
        if (self.whiteToMove and self.currentCastelingRight.wks) or (not self.whiteToMove and self.currentCastelingRight.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.whiteToMove and self.currentCastelingRight.wqs) or (not self.whiteToMove and self.currentCastelingRight.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))
    

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3]:
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))
    
class CastleRights:
    def __init__(self, wks, bks, wqs, bqs) -> None:
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    #  maps keys to values
    #  key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()} #  Reverse the dict

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()} #  Reverse the dict


    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #  Pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        #  Enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        #  Castle Move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #  Give us a unique move id between 0 - 7777


    ''' Overriding the equals method '''
    def __eq__(self, other):
        if isinstance(other, Move): #  Make sure that it is an instance of so it does'nt break
            return self.moveID == other.moveID
        


    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)


    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]