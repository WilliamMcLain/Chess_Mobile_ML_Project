import pieces

class main_play():

    def moveInput(side, piece, start, end):
        valid = pieces.Pieces.prime(side, piece, start, end)
        return valid

    def playGame():
        print("Please choose side: black or white")
        print("enter b or w")
        side = input()

        while True:
            if side not in ("b", "w"):
                print("wrong statement. reinput b or w (lowercase only)")
                side = input()
            else:
                break

        counter = 0
        print("Debug: made midway")

        while counter < 6352:
            print("Input move (piece position position')")
            valid = False
            while not valid:
                print("start.pos")
                moveS = input()

                print("piece")
                piece = input()

                print("end.pos")
                moveE = input()

                if len(moveS) == 2:
                    start = moveS
                if len(piece) == 1:
                    piece = piece
                if len(moveE) == 2:
                    end = moveE

                # Now calls the class-level method instead of a local function
                valid = main_play.moveInput(side, piece, start, end)
                if valid == False:
                    print("sorry, that input wasn't correct")
                else:
                    counter += 1

if __name__ == "__main__":
    main_play.playGame()