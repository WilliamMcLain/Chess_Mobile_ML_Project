import pieces

class main_play():


    

    def playGame():
        def moveInput(side, piece, start, end):
            valid = pieces.Pieces.prime(side, piece, start, end)
            return valid
        print("Please choose side: black or white")
        print("enter b or w")
        side = input()

        while True:
            if side not in ("b", "w"):
                print("wrong statement. reinput b or w (lowerase only)")
                side = input()

            else: 
                break #side will = b or w
        
        #side chosen and onward to piece movement from this point


        #move counter
        counter = 0


        print("Debug: made midway")

        #This will loop over the gameplay and take user input for each more
        while counter < 6352: #this should handle all movement based actions possible
            print("Input move (piece position position')")
            valid = False
            while not valid:
                print("start.pos")
                moveS = input()
                #first check if move is a valid input. Second check if mvove is valid in the scheme
                
                print("piece")
                piece = input()

                print("end.pos")
                moveE = input()


                #handles if the input is the valid scheme (like piece etc etc)
                #I can make this input more robust but right now IDGAF
                if len(moveS) == 2:
                    start = moveS

                if len(piece) == 1:
                    piece = piece

                if len(moveE) == 2:
                    end = moveE
                

                #test validity of the input so it doesnt NEED to be tested within the function just assigned
                valid = moveInput(side, piece, start, end) #if moveInput is deemed qualf true
                if (valid == False):
                    print("sorry, that input wasn't correct") #issue here is that we do not specfiy why
                else:
                    # Debug marked out for testing. This moves the computer piece 1
                    # computer.move()
                    counter += 1 #count each valid move



    
    
    #operates the game and init func
    if __name__ == "__main__":
        playGame()
        
        
        





