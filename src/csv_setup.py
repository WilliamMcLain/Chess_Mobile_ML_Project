import csv
import shutil
import os


class csv_setup():

    # Paths are relative to the chess/ root — adjust if running from src/
    _BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    RESET_FILEPATH = os.path.join(_BASE, 'chess_reset.csv')
    GAME_FILEPATH  = os.path.join(_BASE, 'chess_document.csv')

    @staticmethod
    def setup():
        """Copy the reset board into the active game file."""
        shutil.copyfile(csv_setup.RESET_FILEPATH, csv_setup.GAME_FILEPATH)

    # ── Internal helpers ────────────────────────────────────────────────────

    @staticmethod
    def _pos_to_index(pos):
        """
        Convert chess notation to (row, col) board indices.
        'a1' -> row 0, col 0   (row 0 = rank 1, bottom of board)
        'h8' -> row 7, col 7
        Board is stored rank 1 first in the CSV (row 0 = rank 1).
        """
        col = ord(pos[0].lower()) - ord('a')   # a=0 .. h=7
        row = int(pos[1]) - 1                   # 1=0 .. 8=7
        return row, col

    @staticmethod
    def _read_board():
        """Return the full board as a list of lists."""
        with open(csv_setup.GAME_FILEPATH, 'r') as f:
            return list(csv.reader(f))

    @staticmethod
    def _write_board(board):
        """Write a list-of-lists board back to the CSV."""
        with open(csv_setup.GAME_FILEPATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(board)

    # ── Public API ──────────────────────────────────────────────────────────

    @staticmethod
    def find(pos):
        """
        Return the piece at chess position pos (e.g. 'a2').
        Returns 'e' if the square is empty or pos is out of range.
        Alias kept as findPiecewithSpace for compatibility with pieces.py.
        """
        try:
            row, col = csv_setup._pos_to_index(pos)
            board = csv_setup._read_board()
            cell = board[row][col].strip()
            return cell if cell else 'e'
        except (IndexError, ValueError, FileNotFoundError):
            return 'e'

    @staticmethod
    def findPiecewithSpace(pos):
        """Alias for find() — keeps old call sites working."""
        return csv_setup.find(pos)

    @staticmethod
    def findSpaceofPiece(piece):
        """
        Search the whole board for a piece code (e.g. 'wk').
        Returns the first matching chess position string (e.g. 'e1'),
        or None if the piece is not found.
        """
        board = csv_setup._read_board()
        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if cell.strip() == piece:
                    col_letter = chr(ord('a') + col_idx)
                    row_number = str(row_idx + 1)
                    return col_letter + row_number
        return None

    @staticmethod
    def updateCSV(piece, start, end):
        """
        Move piece from start to end on the board CSV.
        Clears the start square to 'e'.
        piece  — the piece code to write at end (e.g. 'wp')
        start  — chess notation of origin square  (e.g. 'a2')
        end    — chess notation of target square  (e.g. 'a4')
        """
        row_s, col_s = csv_setup._pos_to_index(start)
        row_e, col_e = csv_setup._pos_to_index(end)

        board = csv_setup._read_board()
        board[row_e][col_e] = piece
        board[row_s][col_s] = 'e'
        csv_setup._write_board(board)

    @staticmethod
    def piecelist():
        """Return a flat list of all non-empty cells on the board."""
        board = csv_setup._read_board()
        return [cell.strip() for row in board for cell in row if cell.strip() != 'e']