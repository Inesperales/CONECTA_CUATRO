"""`car_lu` — the Connect Four player of Carmen Cuerva and Lucía Argüello.

How it decides:

* **Bitboards.** The board is turned into two integers (the stones of the side to move,
  and every stone), one bit per cell, column by column with a spare bit on top of each
  column. A line of four is then found with a handful of shifts and ``&``s, so the search
  visits far more positions per second than one that walks lists.
* **Search.** Negamax with alpha-beta pruning and iterative deepening: it searches 1, 2,
  3, ... plies ahead until its time for this move runs out, and plays the best move of
  the deepest search it finished. A transposition table remembers positions already seen
  (the same position is often reached by different move orders), and moves are tried
  best-first: the best move found before, then the moves that create most threats, then
  centre columns.
* **Safety first.** It never plays a move that lets the rival win straight away, blocks
  a rival's immediate win, and knows that two simultaneous threats are a lost position.
* **Evaluation.** At the search horizon it counts *threats*: empty cells that would
  complete a line of four. Threats on the right row parity are worth double: the player
  who moved first profits from threats on odd rows (counting from the bottom), the other
  player from even rows. That is the long-term idea expert players use to win endgames.
* **Clock.** The tournament gives each player 2 s for the whole game. The bot keeps its
  own clock, allows itself at most 1 s per game, and shares it out among the moves it
  still has to play. Near the end of the game it searches to the last move and plays
  perfectly.

Works on any board size, not only 6 x 7, and never modifies the board it receives.
"""

from __future__ import annotations

import time

from conecta_cuatro import game
from conecta_cuatro.game import Move, State
from conecta_cuatro.player import Player

#: Score of a won position (minus the number of stones when it is won: faster wins
#: score higher, slower losses lose less).
WIN = 1_000_000
#: Seconds of thinking the bot allows itself per game (the tournament's budget is 2 s).
GAME_BUDGET_S = 0.9
#: Share of the remaining moves the budget is spread over (< 1 spends more early on,
#: where the search matters most; the endgame is solved exactly and costs little).
SPREAD = 0.35
#: Seconds it may spend on a single move, however much budget is left.
MAX_MOVE_S = 0.15
#: Weight of a threat in the evaluation, and extra weight when it is on a good row.
THREAT = 8
GOOD_ROW = 16
#: Weight of an open two: a line of four with two own stones and no rival stone.
TWO = 2
#: Transposition table size at which it is cleared (keeps memory bounded).
TT_LIMIT = 300_000


class _OutOfTime(Exception):
    """Raised inside the search when the time for this move is over."""


class _Geometry:
    """Precomputed bit masks for one board size."""

    def __init__(self, rows: int, columns: int) -> None:
        self.rows = rows
        self.columns = columns
        self.stride = rows + 1  # one spare bit on top of every column
        self.cells = rows * columns
        self.bottom = sum(1 << (c * self.stride) for c in range(columns))
        self.board = self.bottom * ((1 << rows) - 1)
        self.column_mask = [((1 << rows) - 1) << (c * self.stride) for c in range(columns)]
        # Rows counted from the bottom starting at 1: odd rows are heights 0, 2, 4, ...
        self.odd_rows = sum(
            1 << (c * self.stride + h) for c in range(columns) for h in range(0, rows, 2)
        )
        self.even_rows = self.board ^ self.odd_rows
        centre = columns // 2
        self.centre = self.column_mask[centre]
        self.near_centre = 0
        for c in (centre - 1, centre + 1):
            if 0 <= c < columns and c != centre:
                self.near_centre |= self.column_mask[c]
        # Columns from the centre outwards: the order moves are tried in.
        self.order = sorted(range(columns), key=lambda c: (abs(2 * c - (columns - 1)), c))

    def winning_cells(self, stones: int, mask: int) -> int:
        """Empty cells where ``stones`` would complete a line of four."""
        s = self.stride
        # vertical
        r = (stones << 1) & (stones << 2) & (stones << 3)
        for d in (s, s - 1, s + 1):  # horizontal and both diagonals
            pair = (stones << d) & (stones << (2 * d))
            r |= pair & (stones << (3 * d))
            r |= pair & (stones >> d)
            pair = (stones >> d) & (stones >> (2 * d))
            r |= pair & (stones << d)
            r |= pair & (stones >> (3 * d))
        return r & (self.board ^ mask)

    def open_twos(self, stones: int, rival: int) -> int:
        """Lines of four with exactly two of ``stones`` and no ``rival`` stone in them."""
        free = self.board & ~rival
        s = self.stride
        total = 0
        for d in (1, s, s - 1, s + 1):  # vertical, horizontal and both diagonals
            # Bit i of `window` is set when the four cells i, i+d, i+2d, i+3d are all free
            # of rival stones (the spare top bits keep lines from wrapping around).
            window = free & (free >> d) & (free >> (2 * d)) & (free >> (3 * d))
            a, b, c, e = stones, stones >> d, stones >> (2 * d), stones >> (3 * d)
            two_plus = (a & b) | (a & c) | (a & e) | (b & c) | (b & e) | (c & e)
            three_plus = (a & b & c) | (a & b & e) | (a & c & e) | (b & c & e)
            total += (window & two_plus & ~three_plus).bit_count()
        return total


class CarLu(Player):
    """Bitboard negamax with alpha-beta, iterative deepening and threat parity."""

    def __init__(self) -> None:
        self._spent = 0.0
        self._table: dict[int, tuple[int, int, int, int]] = {}
        self._geometry: _Geometry | None = None
        self._nodes = 0
        self._deadline = 0.0

    @classmethod
    def get_name(cls) -> str:
        return "car_lu"

    @classmethod
    def get_authors(cls) -> list[str]:
        return ["Carmen Cuerva", "Lucía Argüello"]

    @classmethod
    def get_icon(cls) -> str:
        return "🦉"

    @classmethod
    def get_description(cls) -> str:
        return (
            "Bitboard negamax with alpha-beta, iterative deepening and a transposition "
            "table; never gives away an immediate win and scores threats by row parity "
            "(odd rows for the first player, even rows for the second). Plays the endgame "
            "perfectly."
        )

    # ------------------------------------------------------------------ #
    # Entry point                                                        #
    # ------------------------------------------------------------------ #
    def choose_move(self, state: State) -> Move:
        start = time.perf_counter()
        legal = game.legal_moves(state)
        try:
            move = self._think(state, start)
        except Exception:  # never forfeit a game over a bug of our own
            move = None
        if move not in legal:
            move = min(legal, key=lambda c: abs(2 * c - (len(state[0]) - 1)))
        self._spent += time.perf_counter() - start
        return move

    # ------------------------------------------------------------------ #
    # Search                                                             #
    # ------------------------------------------------------------------ #
    def _think(self, state: State, start: float) -> Move | None:
        rows, columns = len(state), len(state[0])
        g = self._geometry
        if g is None or g.rows != rows or g.columns != columns:
            g = self._geometry = _Geometry(rows, columns)
            self._table.clear()
        me = game.current_player(state)
        position = mask = 0
        moves = 0
        for r in range(rows):
            height = rows - 1 - r
            for c in range(columns):
                cell = state[r][c]
                if cell:
                    bit = 1 << (c * g.stride + height)
                    mask |= bit
                    moves += 1
                    if cell == me:
                        position |= bit
        if len(self._table) > TT_LIMIT:
            self._table.clear()

        possible = (mask + g.bottom) & g.board
        playable = [c for c in g.order if possible & g.column_mask[c]]
        if not playable:
            return None
        # Win at once if we can.
        wins = g.winning_cells(position, mask) & possible
        for c in playable:
            if wins & g.column_mask[c]:
                return c

        empty = g.cells - moves
        left = max(0.005, GAME_BUDGET_S - self._spent)
        my_moves_left = max(1, (empty + 1) // 2)
        allowance = min(MAX_MOVE_S, left / max(2.0, SPREAD * my_moves_left))
        self._deadline = start + allowance

        best = self._fallback(g, position, mask, playable)
        for depth in range(1, empty + 1):
            try:
                move, score = self._root(g, position, mask, moves, depth, best)
            except _OutOfTime:
                break
            best = move
            if abs(score) >= WIN - g.cells:  # the game is decided: no need to look further
                break
        return best

    def _fallback(self, g: _Geometry, position: int, mask: int, playable: list[int]) -> int:
        """A move that does not hand the rival an immediate win, if there is one."""
        rival = position ^ mask
        threats = g.winning_cells(rival, mask)
        possible = (mask + g.bottom) & g.board
        forced = threats & possible
        for c in playable:
            if forced & g.column_mask[c]:
                return c
        for c in playable:
            bit = possible & g.column_mask[c]
            if not (threats & (bit << 1)):
                return c
        return playable[0]

    def _root(
        self, g: _Geometry, position: int, mask: int, moves: int, depth: int, first: int
    ) -> tuple[int, int]:
        possible = (mask + g.bottom) & g.board
        order = [first] + [c for c in g.order if c != first]
        best_move, best_score = first, -WIN - 1
        alpha, beta = -WIN - 1, WIN + 1
        for c in order:
            bit = possible & g.column_mask[c]
            if not bit:
                continue
            score = -self._negamax(
                g, position ^ mask, mask | bit, moves + 1, depth - 1, -beta, -alpha
            )
            if score > best_score:
                best_move, best_score = c, score
            if score > alpha:
                alpha = score
        return best_move, best_score

    def _negamax(
        self, g: _Geometry, position: int, mask: int, moves: int, depth: int, alpha: int, beta: int
    ) -> int:
        """Score of the position for the side to move (``position`` are its stones)."""
        self._nodes += 1
        if not self._nodes & 255 and time.perf_counter() > self._deadline:
            raise _OutOfTime
        if moves == g.cells:
            return 0  # draw
        possible = (mask + g.bottom) & g.board
        if g.winning_cells(position, mask) & possible:
            return WIN - (moves + 1)  # we win with our next stone
        rival = position ^ mask
        rival_wins = g.winning_cells(rival, mask)
        forced = possible & rival_wins
        lost = -(WIN - (moves + 2))
        if forced:
            if forced & (forced - 1):
                return lost  # two threats at once: one of them gets through
            possible = forced
        possible &= ~(rival_wins >> 1)  # never play just below a rival's winning cell
        if not possible:
            return lost
        if moves + 1 == g.cells:
            return 0
        if depth <= 0:
            return self._evaluate(g, position, mask, moves)

        key = position + mask
        entry = self._table.get(key)
        tt_move = -1
        if entry is not None:
            e_depth, e_flag, e_value, tt_move = entry
            if e_depth >= depth:
                if e_flag == 0:
                    return e_value
                if e_flag == 1 and e_value >= beta:
                    return e_value
                if e_flag == -1 and e_value <= alpha:
                    return e_value

        # Order: the table's best move, then moves creating most threats, then the centre.
        candidates: list[tuple[int, int, int]] = []
        for rank, c in enumerate(g.order):
            bit = possible & g.column_mask[c]
            if not bit:
                continue
            if c == tt_move:
                priority = 1000
            else:
                priority = g.winning_cells(position | bit, mask | bit).bit_count() * 10 - rank
            candidates.append((priority, c, bit))
        candidates.sort(reverse=True)

        original_alpha = alpha
        best_value, best_move = -WIN - 1, candidates[0][1]
        for _, c, bit in candidates:
            value = -self._negamax(g, rival, mask | bit, moves + 1, depth - 1, -beta, -alpha)
            if value > best_value:
                best_value, best_move = value, c
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
        if best_value <= original_alpha:
            flag = -1  # upper bound
        elif best_value >= beta:
            flag = 1  # lower bound
        else:
            flag = 0  # exact
        self._table[key] = (depth, flag, best_value, best_move)
        return best_value

    def _evaluate(self, g: _Geometry, position: int, mask: int, moves: int) -> int:
        """Heuristic score at the horizon, for the side to move."""
        rival = position ^ mask
        mine = g.winning_cells(position, mask)
        theirs = g.winning_cells(rival, mask)
        first_to_move = moves % 2 == 0  # the side to move played the first stone
        my_rows = g.odd_rows if first_to_move else g.even_rows
        their_rows = g.even_rows if first_to_move else g.odd_rows
        score = THREAT * (mine.bit_count() - theirs.bit_count())
        score += GOOD_ROW * ((mine & my_rows).bit_count() - (theirs & their_rows).bit_count())
        score += TWO * (g.open_twos(position, rival) - g.open_twos(rival, position))
        score += 3 * ((position & g.centre).bit_count() - (rival & g.centre).bit_count())
        score += (position & g.near_centre).bit_count() - (rival & g.near_centre).bit_count()
        return score
