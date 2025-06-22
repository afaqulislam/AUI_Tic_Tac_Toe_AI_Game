from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import uuid

app = Flask(__name__)
CORS(app)

# In-memory game storage (in production, use Redis or database)
games = {}


class TicTacToeGame:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.player_turn = "X"
        self.status = ""
        self.game_over = False
        self.game_id = str(uuid.uuid4())

    def check_win(self, player):
        # Check rows, columns, and diagonals
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)) or all(
                self.board[j][i] == player for j in range(3)
            ):
                return True

        if all(self.board[i][i] == player for i in range(3)) or all(
            self.board[i][2 - i] == player for i in range(3)
        ):
            return True

        return False

    def is_draw(self):
        return all(cell != "" for row in self.board for cell in row)

    def get_empty_cells(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ""]

    def ai_move(self):
        empty_cells = self.get_empty_cells()
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.board[row][col] = "O"

            if self.check_win("O"):
                self.status = "😔 AI Wins!"
                self.game_over = True
            elif self.is_draw():
                self.status = "🤝 Draw!"
                self.game_over = True
            else:
                self.player_turn = "X"

    def make_move(self, row, col):
        if (
            self.board[row][col] == ""
            and not self.game_over
            and self.player_turn == "X"
        ):
            self.board[row][col] = "X"

            if self.check_win("X"):
                self.status = "🎉 You Win!"
                self.game_over = True
            elif self.is_draw():
                self.status = "🤝 Draw!"
                self.game_over = True
            else:
                self.player_turn = "O"
                self.ai_move()

    def to_dict(self):
        return {
            "board": self.board,
            "player_turn": self.player_turn,
            "status": self.status,
            "game_over": self.game_over,
            "game_id": self.game_id,
        }


# Global game instance (in production, use session management)
current_game = TicTacToeGame()


@app.route("/api/init", methods=["POST"])
def init_game():
    global current_game
    current_game = TicTacToeGame()
    return jsonify(current_game.to_dict())


@app.route("/api/move", methods=["POST"])
def make_move():
    global current_game
    data = request.get_json()
    row = data.get("row")
    col = data.get("col")

    if row is None or col is None:
        return jsonify({"error": "Invalid move data"}), 400

    current_game.make_move(row, col)
    return jsonify(current_game.to_dict())


@app.route("/api/reset", methods=["POST"])
def reset_game():
    global current_game
    current_game = TicTacToeGame()
    return jsonify(current_game.to_dict())


@app.route("/api/status", methods=["GET"])
def get_status():
    global current_game
    return jsonify(current_game.to_dict())


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Tic Tac Toe API is running"})


if __name__ == "__main__":
    print("Starting Tic Tac Toe Python Backend...")
    print("API endpoints:")
    print("- POST /api/init - Initialize new game")
    print("- POST /api/move - Make a move")
    print("- POST /api/reset - Reset game")
    print("- GET /api/status - Get game status")
    print("- GET /health - Health check")
    app.run(debug=True, host="0.0.0.0", port=5000)
