import pieces

class main():
    def playGame():
        
        print("Please choose side: black or white")
        print("enter b or w")
        side = "h"
        
        while True:
            side = input() 

            if side != "b" or "w":
                print("wrong statement")

            else: 
                break #side will = b or w
        
        #move counter
        counter == 0

        while counter < 6351: #this should handle all movement based actions
            print("Input move (piece position position')")
            valid = False
            while not valid:
                move = input()
                #first check if move is a valid input. Second check if mvove is valid in the scheme
                
                #handles if the input is the valid scheme (like piece etc etc)
                #I can make this input more robust but right now IDGAF
                try:
                    piece = substring(0)
                    start = substring(2,3)
                    end = substring (5,6)
                except:
                    print("wrong input")

                valid == moveInput(side, piece, start, end) #if moveInput is deemed qualf true
                if (valid == False):
                    print("sorry, that input wasn't correct") #issue here is that we do not specfiy why
    
            counter = counter + 1 #count each move
    def moveInput(side, piece, start, end):
        valid = pieces(prime(side, piece, start, end))
        return valid



        
        
        





