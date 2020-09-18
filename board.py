import pygame as p
import chessEngine

p.init()
width = height = 500
dimension = 8
maxfps = 15
sqSize = height // dimension
images = {}


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (sqSize, sqSize))


def main():
    p.init()
    screen = p.display.set_mode((width, height))
    screen.fill(p.Color("white"))
    gs = chessEngine.GameStart()
    print(gs.board)
    load_images()
    clock = p.time.Clock()
    movesvalid = gs.valid_moves()
    move_made = False  # flag variable when a move is made
    sq_selected = ()  # no square selected, keep track the last click of the user (tuple (row, col))
    player_clicks = []  # keep track the player clicks (two tuples (6,4) (4,4))
    moving = True
    while moving:
        for e in p.event.get():
            if e.type == p.QUIT:
                moving = False

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//sqSize
                row = location[1]//sqSize
                if sq_selected == (row, col):
                    sq_selected = ()  # de select
                    player_clicks = []  # clear player clicks
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)  # adding 1st and 2nd clicks
                if len(player_clicks) == 2:
                    move = chessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation())
                    for i in range(len(movesvalid)):
                        if move == movesvalid[i]:
                            gs.make_move(movesvalid[i])
                            move_made = True
                            sq_selected = ()
                            player_clicks = []
                    if not move_made:
                        player_clicks = [sq_selected]
            #  key handle
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when press z key
                    gs.undo_move()
                    move_made = True
        if move_made:
            movesvalid = gs.valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(maxfps)
        p.display.flip()


def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    colors = [p.Color("white"), p.Color("light gray")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]  # 2nd row 5th column = 7 // 2 = 3 light gray color
            p.draw.rect(screen, color, p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))


def draw_pieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))


if __name__ == '__main__':
    main()

