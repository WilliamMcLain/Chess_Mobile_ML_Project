import unittest
from unittest.mock import MagicMock
import sys
import os

# ── Path setup ────────────────────────────────────────────────────────────────
# This file lives in chess/test/ — add chess/src/ so imports resolve
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
sys.path.insert(0, os.path.abspath(SRC))

# ── Mock csv_setup so tests don't need real CSV files ─────────────────────────
csv_mock = MagicMock()
sys.modules['csv_setup'] = csv_mock
sys.modules['pandas']    = MagicMock()

# board_state is a flat dict: {'a2': 'wp', 'a3': 'e', ...}
board_state = {}

def mock_find(pos):
    return board_state.get(pos, 'e')

csv_mock.csv_setup.find             = mock_find
csv_mock.csv_setup.findPiecewithSpace = mock_find
csv_mock.csv_setup.updateCSV        = MagicMock(return_value=True)

import importlib
import pieces
importlib.reload(pieces)
from pieces import Pieces

# ── Helper ────────────────────────────────────────────────────────────────────

def set_board(state: dict):
    """Set the mocked board state for a test."""
    board_state.clear()
    board_state.update(state)


# ═════════════════════════════════════════════════════════════════════════════
# 1. INPUT VALIDATION
# ═════════════════════════════════════════════════════════════════════════════

class TestInputChess(unittest.TestCase):
    """inputChess() — validates raw user input before any chess logic runs."""

    def test_valid_pawn_move(self):
        self.assertTrue(Pieces.inputChess('w', 'p', 'a2', 'a3'))

    def test_valid_knight_move(self):
        self.assertTrue(Pieces.inputChess('w', 'h', 'b1', 'c3'))

    def test_valid_queen_move(self):
        self.assertTrue(Pieces.inputChess('b', 'q', 'd8', 'd1'))

    def test_all_valid_piece_letters(self):
        for p in ['k', 'q', 'b', 'c', 'h', 'p', 's']:
            with self.subTest(piece=p):
                self.assertTrue(Pieces.inputChess('w', p, 'a1', 'b2'))

    def test_all_valid_columns(self):
        for col in 'abcdefgh':
            with self.subTest(col=col):
                self.assertTrue(Pieces.inputChess('w', 'p', f'{col}2', f'{col}3'))

    def test_all_valid_rows(self):
        for row in '12345678':
            with self.subTest(row=row):
                self.assertTrue(Pieces.inputChess('w', 'p', f'a{row}', f'b{row}'))

    def test_invalid_piece_letter(self):
        self.assertFalse(Pieces.inputChess('w', 'x', 'a2', 'a3'))

    def test_invalid_piece_number(self):
        self.assertFalse(Pieces.inputChess('w', '1', 'a2', 'a3'))

    def test_invalid_start_column_out_of_range(self):
        self.assertFalse(Pieces.inputChess('w', 'p', 'z2', 'a3'))

    def test_invalid_start_row_too_high(self):
        self.assertFalse(Pieces.inputChess('w', 'p', 'a9', 'a3'))

    def test_invalid_start_row_zero(self):
        self.assertFalse(Pieces.inputChess('w', 'p', 'a0', 'a3'))

    def test_invalid_end_column(self):
        self.assertFalse(Pieces.inputChess('w', 'p', 'a2', 'z3'))

    def test_invalid_end_row_too_high(self):
        self.assertFalse(Pieces.inputChess('w', 'p', 'a2', 'a9'))


# ═════════════════════════════════════════════════════════════════════════════
# 2. WHITE PAWN
# ═════════════════════════════════════════════════════════════════════════════

class TestWhitePawn(unittest.TestCase):
    """White pawn: moves up the board (increasing row number in notation)."""

    def test_single_step_forward_clear(self):
        set_board({'a2': 'wp', 'a3': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'p', 'a2', 'a3'))

    def test_single_step_forward_blocked(self):
        set_board({'a2': 'wp', 'a3': 'bp'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a2', 'a3'))

    def test_double_step_from_start_clear(self):
        set_board({'a2': 'wp', 'a3': 'e', 'a4': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'p', 'a2', 'a4'))

    def test_double_step_blocked_on_intermediate_square(self):
        set_board({'a2': 'wp', 'a3': 'bp', 'a4': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a2', 'a4'))

    def test_double_step_blocked_on_destination(self):
        set_board({'a2': 'wp', 'a3': 'e', 'a4': 'bp'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a2', 'a4'))

    def test_double_step_only_from_row_2(self):
        set_board({'a4': 'wp', 'a5': 'e', 'a6': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a4', 'a6'))

    def test_diagonal_capture_right(self):
        set_board({'a2': 'wp', 'b3': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'p', 'a2', 'b3'))

    def test_diagonal_capture_left(self):
        set_board({'c2': 'wp', 'b3': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'p', 'c2', 'b3'))

    def test_diagonal_capture_empty_square_illegal(self):
        set_board({'a2': 'wp', 'b3': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a2', 'b3'))

    def test_cannot_capture_own_piece_diagonal(self):
        set_board({'a2': 'wp', 'b3': 'wp'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a2', 'b3'))

    def test_cannot_move_backward(self):
        set_board({'a3': 'wp', 'a2': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a3', 'a2'))

    def test_cannot_move_sideways(self):
        set_board({'a2': 'wp', 'b2': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a2', 'b2'))

    def test_cannot_move_three_squares(self):
        set_board({'a2': 'wp', 'a3': 'e', 'a4': 'e', 'a5': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'p', 'a2', 'a5'))


# ═════════════════════════════════════════════════════════════════════════════
# 3. BLACK PAWN
# ═════════════════════════════════════════════════════════════════════════════

class TestBlackPawn(unittest.TestCase):
    """Black pawn: moves down the board (decreasing row number in notation)."""

    def test_single_step_forward_clear(self):
        set_board({'a7': 'bp', 'a6': 'e'})
        self.assertTrue(Pieces.isMoveValid('b', 'p', 'a7', 'a6'))

    def test_single_step_forward_blocked(self):
        set_board({'a7': 'bp', 'a6': 'wp'})
        self.assertFalse(Pieces.isMoveValid('b', 'p', 'a7', 'a6'))

    def test_double_step_from_start_clear(self):
        set_board({'a7': 'bp', 'a6': 'e', 'a5': 'e'})
        self.assertTrue(Pieces.isMoveValid('b', 'p', 'a7', 'a5'))

    def test_double_step_blocked_on_intermediate(self):
        set_board({'a7': 'bp', 'a6': 'wp', 'a5': 'e'})
        self.assertFalse(Pieces.isMoveValid('b', 'p', 'a7', 'a5'))

    def test_double_step_only_from_row_7(self):
        set_board({'a5': 'bp', 'a4': 'e', 'a3': 'e'})
        self.assertFalse(Pieces.isMoveValid('b', 'p', 'a5', 'a3'))

    def test_diagonal_capture(self):
        set_board({'a7': 'bp', 'b6': 'wp'})
        self.assertTrue(Pieces.isMoveValid('b', 'p', 'a7', 'b6'))

    def test_diagonal_capture_empty_illegal(self):
        set_board({'a7': 'bp', 'b6': 'e'})
        self.assertFalse(Pieces.isMoveValid('b', 'p', 'a7', 'b6'))

    def test_cannot_capture_own_piece(self):
        set_board({'a7': 'bp', 'b6': 'bp'})
        self.assertFalse(Pieces.isMoveValid('b', 'p', 'a7', 'b6'))

    def test_cannot_move_upward(self):
        set_board({'a6': 'bp', 'a7': 'e'})
        self.assertFalse(Pieces.isMoveValid('b', 'p', 'a6', 'a7'))


# ═════════════════════════════════════════════════════════════════════════════
# 4. KNIGHT
# ═════════════════════════════════════════════════════════════════════════════

class TestKnight(unittest.TestCase):
    """Knight: L-shape moves, jumps over pieces."""

    def test_valid_L_up2_right1(self):
        set_board({'b1': 'wh', 'c3': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'h', 'b1', 'c3'))

    def test_valid_L_up1_right2(self):
        set_board({'b1': 'wh', 'd2': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'h', 'b1', 'd2'))

    def test_all_8_L_shapes_from_center(self):
        offsets = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for dr, dc in offsets:
            sr, sc = 4, 4
            er, ec = sr+dr, sc+dc
            start = chr(97+sc) + str(8-sr)
            end   = chr(97+ec) + str(8-er)
            set_board({start: 'wh', end: 'e'})
            with self.subTest(offset=(dr,dc)):
                self.assertTrue(Pieces.isMoveValid('w', 'h', start, end))

    def test_knight_jumps_over_blocking_pieces(self):
        # Squares between b1 and c3 are occupied — knight ignores them
        set_board({'b1': 'wh', 'b2': 'wp', 'c2': 'wp', 'c3': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'h', 'b1', 'c3'))

    def test_cannot_move_straight(self):
        set_board({'b1': 'wh', 'b3': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'h', 'b1', 'b3'))

    def test_cannot_move_diagonal(self):
        set_board({'b1': 'wh', 'c2': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'h', 'b1', 'c2'))

    def test_cannot_land_on_own_piece(self):
        set_board({'b1': 'wh', 'c3': 'wp'})
        self.assertFalse(Pieces.isMoveValid('w', 'h', 'b1', 'c3'))

    def test_can_capture_enemy(self):
        set_board({'b1': 'wh', 'c3': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'h', 'b1', 'c3'))

    def test_black_knight_all_8(self):
        offsets = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for dr, dc in offsets:
            sr, sc = 4, 4
            er, ec = sr+dr, sc+dc
            start = chr(97+sc) + str(8-sr)
            end   = chr(97+ec) + str(8-er)
            set_board({start: 'bh', end: 'e'})
            with self.subTest(offset=(dr,dc)):
                self.assertTrue(Pieces.isMoveValid('b', 'h', start, end))


# ═════════════════════════════════════════════════════════════════════════════
# 5. BISHOP
# ═════════════════════════════════════════════════════════════════════════════

class TestBishop(unittest.TestCase):
    """Bishop: diagonal only, blocked by intervening pieces."""

    def test_short_diagonal_clear(self):
        set_board({'a1': 'wb', 'c3': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'b', 'a1', 'c3'))

    def test_short_diagonal_blocked(self):
        set_board({'a1': 'wb', 'b2': 'wp', 'c3': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'b', 'a1', 'c3'))

    def test_long_diagonal_clear(self):
        set_board({'a1': 'wb', 'h8': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'b', 'a1', 'h8'))

    def test_long_diagonal_blocked_midway(self):
        set_board({'a1': 'wb', 'd4': 'wp', 'h8': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'b', 'a1', 'h8'))

    def test_cannot_move_straight(self):
        set_board({'a1': 'wb', 'a5': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'b', 'a1', 'a5'))

    def test_cannot_move_horizontal(self):
        set_board({'a1': 'wb', 'e1': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'b', 'a1', 'e1'))

    def test_can_capture_enemy_diagonal(self):
        set_board({'a1': 'wb', 'c3': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'b', 'a1', 'c3'))

    def test_cannot_capture_own_diagonal(self):
        set_board({'a1': 'wb', 'c3': 'wp'})
        self.assertFalse(Pieces.isMoveValid('w', 'b', 'a1', 'c3'))

    def test_all_four_diagonal_directions(self):
        directions = [('d4','f6'),('d4','b6'),('d4','f2'),('d4','b2')]
        for start, end in directions:
            set_board({start: 'wb', end: 'e'})
            with self.subTest(start=start, end=end):
                self.assertTrue(Pieces.isMoveValid('w', 'b', start, end))


# ═════════════════════════════════════════════════════════════════════════════
# 6. ROOK
# ═════════════════════════════════════════════════════════════════════════════

class TestRook(unittest.TestCase):
    """Rook: straight lines only, blocked by intervening pieces."""

    def test_move_full_row_clear(self):
        set_board({'a1': 'wc', 'h1': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'c', 'a1', 'h1'))

    def test_move_full_column_clear(self):
        set_board({'a1': 'wc', 'a8': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'c', 'a1', 'a8'))

    def test_blocked_along_row(self):
        set_board({'a1': 'wc', 'd1': 'wp', 'h1': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'c', 'a1', 'h1'))

    def test_blocked_along_column(self):
        set_board({'a1': 'wc', 'a4': 'bp', 'a8': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'c', 'a1', 'a8'))

    def test_cannot_move_diagonal(self):
        set_board({'a1': 'wc', 'c3': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'c', 'a1', 'c3'))

    def test_capture_enemy_at_end_of_row(self):
        set_board({'a1': 'wc', 'h1': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'c', 'a1', 'h1'))

    def test_cannot_capture_own_piece(self):
        set_board({'a1': 'wc', 'a8': 'wp'})
        self.assertFalse(Pieces.isMoveValid('w', 'c', 'a1', 'a8'))

    def test_one_square_move(self):
        set_board({'a1': 'wc', 'b1': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'c', 'a1', 'b1'))


# ═════════════════════════════════════════════════════════════════════════════
# 7. QUEEN
# ═════════════════════════════════════════════════════════════════════════════

class TestQueen(unittest.TestCase):
    """Queen: rook + bishop combined."""

    def test_move_straight_clear(self):
        set_board({'a1': 'wq', 'a8': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'q', 'a1', 'a8'))

    def test_move_diagonal_clear(self):
        set_board({'a1': 'wq', 'd4': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'q', 'a1', 'd4'))

    def test_blocked_straight(self):
        set_board({'a1': 'wq', 'a4': 'wp', 'a8': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'q', 'a1', 'a8'))

    def test_blocked_diagonal(self):
        set_board({'a1': 'wq', 'b2': 'wp', 'd4': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'q', 'a1', 'd4'))

    def test_cannot_move_L_shape(self):
        set_board({'a1': 'wq', 'c2': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'q', 'a1', 'c2'))

    def test_capture_enemy_straight(self):
        set_board({'a1': 'wq', 'a8': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'q', 'a1', 'a8'))

    def test_capture_enemy_diagonal(self):
        set_board({'a1': 'wq', 'd4': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'q', 'a1', 'd4'))

    def test_cannot_capture_own(self):
        set_board({'a1': 'wq', 'd4': 'wp'})
        self.assertFalse(Pieces.isMoveValid('w', 'q', 'a1', 'd4'))


# ═════════════════════════════════════════════════════════════════════════════
# 8. KING
# ═════════════════════════════════════════════════════════════════════════════

class TestKing(unittest.TestCase):
    """King: one square in any direction."""

    def test_move_one_forward(self):
        set_board({'a1': 'wk', 'a2': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'k', 'a1', 'a2'))

    def test_move_one_diagonal(self):
        set_board({'a1': 'wk', 'b2': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'k', 'a1', 'b2'))

    def test_move_one_sideways(self):
        set_board({'b1': 'wk', 'a1': 'e'})
        self.assertTrue(Pieces.isMoveValid('w', 'k', 'b1', 'a1'))

    def test_cannot_move_two_squares_straight(self):
        set_board({'a1': 'wk', 'a3': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'k', 'a1', 'a3'))

    def test_cannot_move_two_squares_diagonal(self):
        set_board({'a1': 'wk', 'c3': 'e'})
        self.assertFalse(Pieces.isMoveValid('w', 'k', 'a1', 'c3'))

    def test_cannot_stay_in_place(self):
        set_board({'a1': 'wk'})
        self.assertFalse(Pieces.isMoveValid('w', 'k', 'a1', 'a1'))

    def test_can_capture_enemy(self):
        set_board({'a1': 'wk', 'b2': 'bp'})
        self.assertTrue(Pieces.isMoveValid('w', 'k', 'a1', 'b2'))

    def test_cannot_capture_own_piece(self):
        set_board({'a1': 'wk', 'b2': 'wp'})
        self.assertFalse(Pieces.isMoveValid('w', 'k', 'a1', 'b2'))

    def test_all_8_directions_clear(self):
        for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            sr, sc = 4, 4
            er, ec = sr+dr, sc+dc
            start = chr(97+sc)+str(8-sr)
            end   = chr(97+ec)+str(8-er)
            set_board({start:'wk', end:'e'})
            with self.subTest(dir=(dr,dc)):
                self.assertTrue(Pieces.isMoveValid('w', 'k', start, end))


# ═════════════════════════════════════════════════════════════════════════════
# 9. PATH CLEAR UTILITY
# ═════════════════════════════════════════════════════════════════════════════

class TestIsPathClear(unittest.TestCase):
    """is_path_clear() — checks squares between start and end (exclusive)."""

    def test_clear_horizontal_full_row(self):
        set_board({})
        self.assertTrue(Pieces.is_path_clear('a1', 'h1'))

    def test_blocked_horizontal(self):
        set_board({'d1': 'wp'})
        self.assertFalse(Pieces.is_path_clear('a1', 'h1'))

    def test_clear_vertical_full_column(self):
        set_board({})
        self.assertTrue(Pieces.is_path_clear('a1', 'a8'))

    def test_blocked_vertical(self):
        set_board({'a5': 'bp'})
        self.assertFalse(Pieces.is_path_clear('a1', 'a8'))

    def test_clear_diagonal(self):
        set_board({})
        self.assertTrue(Pieces.is_path_clear('a1', 'd4'))

    def test_blocked_diagonal(self):
        set_board({'b2': 'wp'})
        self.assertFalse(Pieces.is_path_clear('a1', 'd4'))

    def test_adjacent_horizontal_always_clear(self):
        set_board({})
        self.assertTrue(Pieces.is_path_clear('a1', 'b1'))

    def test_adjacent_vertical_always_clear(self):
        set_board({})
        self.assertTrue(Pieces.is_path_clear('a1', 'a2'))

    def test_adjacent_diagonal_always_clear(self):
        set_board({})
        self.assertTrue(Pieces.is_path_clear('a1', 'b2'))

    def test_blocker_at_start_ignored(self):
        # Start square itself should not count as a blocker
        set_board({'a1': 'wc'})
        self.assertTrue(Pieces.is_path_clear('a1', 'a4'))

    def test_blocker_at_end_ignored(self):
        # End square is a capture target — path check excludes it
        set_board({'a4': 'bp'})
        self.assertTrue(Pieces.is_path_clear('a1', 'a4'))


# ═════════════════════════════════════════════════════════════════════════════
# 10. END-TO-END via prime()
# ═════════════════════════════════════════════════════════════════════════════

class TestPrime(unittest.TestCase):
    """prime() — the function main_play.py calls. Tests the full pipeline."""

    def test_valid_white_pawn_move(self):
        set_board({'a2': 'wp', 'a3': 'e'})
        self.assertTrue(Pieces.prime('w', 'p', 'a2', 'a3'))

    def test_valid_black_pawn_move(self):
        set_board({'a7': 'bp', 'a6': 'e'})
        self.assertTrue(Pieces.prime('b', 'p', 'a7', 'a6'))

    def test_wrong_piece_at_position_fails_in_move(self):
        # Board has a rook at a2, but we claim it's a pawn
        set_board({'a2': 'wc', 'a3': 'e'})
        self.assertFalse(Pieces.prime('w', 'p', 'a2', 'a3'))

    def test_bad_piece_letter_fails_in_inputChess(self):
        self.assertFalse(Pieces.prime('w', 'z', 'a2', 'a3'))

    def test_illegal_move_fails_in_isMoveValid(self):
        # Pawn cannot jump 3 squares
        set_board({'a2': 'wp', 'a3': 'e', 'a4': 'e', 'a5': 'e'})
        self.assertFalse(Pieces.prime('w', 'p', 'a2', 'a5'))

    def test_updateCSV_called_on_valid_move(self):
        set_board({'a2': 'wp', 'a3': 'e'})
        csv_mock.csv_setup.updateCSV.reset_mock()
        Pieces.prime('w', 'p', 'a2', 'a3')
        csv_mock.csv_setup.updateCSV.assert_called_once()

    def test_updateCSV_not_called_on_invalid_move(self):
        set_board({'a2': 'wp', 'a5': 'e'})
        csv_mock.csv_setup.updateCSV.reset_mock()
        Pieces.prime('w', 'p', 'a2', 'a5')
        csv_mock.csv_setup.updateCSV.assert_not_called()

    def test_valid_knight_e2e(self):
        set_board({'b1': 'wh', 'c3': 'e'})
        self.assertTrue(Pieces.prime('w', 'h', 'b1', 'c3'))

    def test_valid_rook_e2e(self):
        set_board({'a1': 'wc', 'a5': 'e'})
        self.assertTrue(Pieces.prime('w', 'c', 'a1', 'a5'))


# ═════════════════════════════════════════════════════════════════════════════
# Runner
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    classes = [
        TestInputChess,
        TestWhitePawn, TestBlackPawn,
        TestKnight, TestBishop,
        TestRook, TestQueen, TestKing,
        TestIsPathClear, TestPrime,
    ]
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)