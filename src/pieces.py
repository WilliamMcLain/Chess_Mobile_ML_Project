import csv_setup
import string

class Pieces():

    @staticmethod
    def prime(side, piece, start, end):
        print("Debug: Here")
        if not Pieces.inputChess(side, piece, start, end):
            print("Debug: inputChess failed")
            return False
        if not Pieces.move(side, piece, start, end):
            print("Debug: move failed")
            return False
        Pieces.updateChess(side, piece, start, end)
        return True

    @staticmethod
    def inputChess(side, piece, start, end):
        pieceAlphabet = ['k', 'q', 'b', 'c', 'h', 'p', 's']
        letterAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        numberAlphabet = ['1', '2', '3', '4', '5', '6', '7', '8']
        if piece not in pieceAlphabet:
            print("Debug: bad piece")
            return False
        if start[0] not in letterAlphabet or start[1] not in numberAlphabet:
            print("Debug: bad start")
            return False
        if end[0] not in letterAlphabet or end[1] not in numberAlphabet:
            print("Debug: bad end")
            return False
        return True

    @staticmethod
    def move(side, piece, start, end):
        # Check piece is actually at start
        boardPiece = csv_setup.csv_setup.find(start)
        expectedPiece = side + piece
        if boardPiece != expectedPiece:
            print(f"Debug: piece mismatch. Board has '{boardPiece}', expected '{expectedPiece}'")
            return False
        if not Pieces.isMoveValid(side, piece, start, end):
            print("Debug: isMoveValid failed")
            return False
        return True

    @staticmethod
    def isMoveValid(side, piece, start, end):
        rowDiff = int(end[1]) - int(start[1])
        colDiff = ord(end[0]) - ord(start[0])

        if side == 'w':
            # --- WHITE PAWN ---
            if piece in ('p', 's'):
                # Regular move forward 1
                if rowDiff == 1 and colDiff == 0:
                    if csv_setup.csv_setup.find(end) == 'e':
                        return True
                    return False

                # Double move from start row
                if rowDiff == 2 and colDiff == 0 and int(start[1]) == 2:
                    mid = end[0] + str(int(start[1]) + 1)
                    if csv_setup.csv_setup.find(end) == 'e' and csv_setup.csv_setup.find(mid) == 'e':
                        return True
                    return False

                # Diagonal capture
                if rowDiff == 1 and abs(colDiff) == 1:
                    target = csv_setup.csv_setup.find(end)
                    if target != 'e' and target.startswith('b'):
                        return True
                    # En passant
                    if piece == 's' and int(start[1]) == 5:
                        below = end[0] + str(int(end[1]) - 1)
                        if csv_setup.csv_setup.find(below) == 'bp':
                            return True
                    return False

                return False

            # --- WHITE BISHOP ---
            elif piece == 'b':
                if rowDiff == 0 or colDiff == 0:
                    return False
                if abs(rowDiff) != abs(colDiff):
                    return False
                if not Pieces.is_path_clear(start, end):
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('w'):
                    return False
                return True

            # --- WHITE KNIGHT ---
            elif piece == 'h':
                if sorted([abs(rowDiff), abs(colDiff)]) != [1, 2]:
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('w'):
                    return False
                return True

            # --- WHITE ROOK ---
            elif piece == 'c':
                if rowDiff != 0 and colDiff != 0:
                    return False
                if not Pieces.is_path_clear(start, end):
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('w'):
                    return False
                return True

            # --- WHITE QUEEN ---
            elif piece == 'q':
                is_diagonal = abs(rowDiff) == abs(colDiff) and rowDiff != 0
                is_straight = (rowDiff == 0) != (colDiff == 0)
                if not is_diagonal and not is_straight:
                    return False
                if not Pieces.is_path_clear(start, end):
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('w'):
                    return False
                return True

            # --- WHITE KING ---
            elif piece == 'k':
                if abs(rowDiff) > 1 or abs(colDiff) > 1:
                    return False
                if rowDiff == 0 and colDiff == 0:
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('w'):
                    return False
                # Reject if destination is attacked by black
                if Pieces.is_square_attacked(end, by_side='b'):
                    return False
                return True

        elif side == 'b':
            # --- BLACK PAWN ---
            if piece in ('p', 's'):
                # Regular move forward 1 (downward for black)
                if rowDiff == -1 and colDiff == 0:
                    if csv_setup.csv_setup.find(end) == 'e':
                        return True
                    return False

                # Double move from start row
                if rowDiff == -2 and colDiff == 0 and int(start[1]) == 7:
                    mid = end[0] + str(int(start[1]) - 1)
                    if csv_setup.csv_setup.find(end) == 'e' and csv_setup.csv_setup.find(mid) == 'e':
                        return True
                    return False

                # Diagonal capture
                if rowDiff == -1 and abs(colDiff) == 1:
                    target = csv_setup.csv_setup.find(end)
                    if target != 'e' and target.startswith('w'):
                        return True
                    # En passant
                    if piece == 's' and int(start[1]) == 4:
                        above = end[0] + str(int(end[1]) + 1)
                        if csv_setup.csv_setup.find(above) == 'wp':
                            return True
                    return False

                return False

            # --- BLACK BISHOP ---
            elif piece == 'b':
                if rowDiff == 0 or colDiff == 0:
                    return False
                if abs(rowDiff) != abs(colDiff):
                    return False
                if not Pieces.is_path_clear(start, end):
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('b'):
                    return False
                return True

            # --- BLACK KNIGHT ---
            elif piece == 'h':
                if sorted([abs(rowDiff), abs(colDiff)]) != [1, 2]:
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('b'):
                    return False
                return True

            # --- BLACK ROOK ---
            elif piece == 'c':
                if rowDiff != 0 and colDiff != 0:
                    return False
                if not Pieces.is_path_clear(start, end):
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('b'):
                    return False
                return True

            # --- BLACK QUEEN ---
            elif piece == 'q':
                is_diagonal = abs(rowDiff) == abs(colDiff) and rowDiff != 0
                is_straight = (rowDiff == 0) != (colDiff == 0)
                if not is_diagonal and not is_straight:
                    return False
                if not Pieces.is_path_clear(start, end):
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('b'):
                    return False
                return True

            # --- BLACK KING ---
            elif piece == 'k':
                if abs(rowDiff) > 1 or abs(colDiff) > 1:
                    return False
                if rowDiff == 0 and colDiff == 0:
                    return False
                target = csv_setup.csv_setup.find(end)
                if target != 'e' and target.startswith('b'):
                    return False
                # Reject if destination is attacked by white
                if Pieces.is_square_attacked(end, by_side='w'):
                    return False
                return True

        return False

    @staticmethod
    def is_path_clear(start, end):
        """Check all squares between start and end are empty (exclusive of both ends)."""
        rowDiff = int(end[1]) - int(start[1])
        colDiff = ord(end[0]) - ord(start[0])

        row_step = 0 if rowDiff == 0 else (1 if rowDiff > 0 else -1)
        col_step = 0 if colDiff == 0 else (1 if colDiff > 0 else -1)

        steps = max(abs(rowDiff), abs(colDiff))
        for i in range(1, steps):  # exclude start and end
            col = chr(ord(start[0]) + col_step * i)
            row = str(int(start[1]) + row_step * i)
            square = col + row
            if csv_setup.csv_setup.find(square) != 'e':
                print(f"Debug: path blocked at {square}")
                return False
        return True

    @staticmethod
    def is_square_attacked(square, by_side, board_state=None):
        """Returns True if `square` is attacked by any piece of `by_side`."""
        files = 'abcdefgh'
        enemy = by_side

        def find(pos):
            return csv_setup.csv_setup.find(pos)

        fi = ord(square[0]) - ord('a')
        ri = int(square[1]) - 1

        def ib(f, r): return 0 <= f < 8 and 0 <= r < 8
        def sq(f, r): return files[f] + str(r + 1)

        # Check pawns
        pawn_dir = -1 if enemy == 'w' else 1  # direction pawns attack FROM
        for df in [-1, 1]:
            f, r = fi + df, ri + pawn_dir
            if ib(f, r):
                p = find(sq(f, r))
                if p == enemy + 'p' or p == enemy + 's':
                    return True

        # Check knights
        for df, dr in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            f, r = fi + df, ri + dr
            if ib(f, r) and find(sq(f, r)) == enemy + 'h':
                return True

        # Check king
        for df, dr in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            f, r = fi + df, ri + dr
            if ib(f, r) and find(sq(f, r)) == enemy + 'k':
                return True

        # Check sliding pieces (rook, queen along ranks/files)
        for df, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
            f, r = fi + df, ri + dr
            while ib(f, r):
                p = find(sq(f, r))
                if p != 'e':
                    if p in (enemy+'c', enemy+'q'):
                        return True
                    break
                f += df; r += dr

        # Check sliding pieces (bishop, queen along diagonals)
        for df, dr in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            f, r = fi + df, ri + dr
            while ib(f, r):
                p = find(sq(f, r))
                if p != 'e':
                    if p in (enemy+'b', enemy+'q'):
                        return True
                    break
                f += df; r += dr

        return False

    @staticmethod
    def updateChess(side, piece, start, end):
        csv_setup.csv_setup.updateCSV(side + piece, start, end)