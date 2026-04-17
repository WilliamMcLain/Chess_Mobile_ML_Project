import csv_setup
import pandas
import string

#all of the pieces exist on the board. We want to define
#1 how they move
#2 where they are
#call/return structure would be okay 
#position data can be in (x,y). We can pass as a string 

class Pieces():
    #def to define if the input is correct
    #def to check if the move is legal
    #def to actually do the move if all true
    def prime(side, piece, start, end):
        valid = inputChess(piece, start, end)
        if valid == True:
            valid = move(piece, start, end)
            if valid == True:
                valid = updateChess(piece, start, end) #updates piece
                return valid
            else:
                return valid
        else:
            return valid
        #so this DSA is gross and sucks, I will redo it later
        #I could sub nest them, this is also a bad approach. I think a while loop or a counter is good
    
    #is the input legal
    def inputChess(side, piece, start, end):
        pieceAlphabet = ['k', 'q', 'b', 'r', 'h', 'p']
        letterAlphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        numberAlphabet = ['1', '2', '3', '4', '5', '6', '7', '8']
        if piece.isin(pieceAlphabet):
            let1 = start[0] #letter 1
            num1 = start[1] #number 1
            if let1.isin(letterAlphabet) and num1.isin(numberAlphabet):
                let2 = end[0] #letter 2
                num2 = end[1] #number 2
                if let2.isin(letterAlphabet) and num2.isin(numberAlphabet):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    #can the move be performed
    def move(side, piece, start, end):
        #part 1) check if piece is in the spot that it believe it is in
        if piece == csv_setup(find(start)): #the piece is in the spot it is assumed to be in
            #part 2) check if piece can be moved to the end point
            if isMoveValid(side, piece, start, end):
                updateChess(side, piece, start, end)
            else:
                return False
        else:
            return False

        
    def isMoveValid(side, piece, start, end):
        match side:
            case 'w':
                match piece:
                    case 'p' | 'pp':
                        #2 out on start (complete)
                        #if pawn is in starting position, end position can be 2 out
                        if(abs(int(end[1])-int(start[1])) == 2):
                            if(int(start[1]) == 2):
                                pos = csv_setup(find(end))
                                let = end[0]
                                num = end[1] - 1
                                pospre = let + num
                                pospreP = csv_setup(find(pospre))
                                #check if move is legal
                                if(pos == 'e' and pospreP == 'e'):
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        else:
                            return False
                        #en passant (complete)
                        #checking row movement first
                        if(int(start[1]==6) and (int(end[1]==7))):
                            #check column either 1 left or 1 right
                            if(abs(ord(start[0]) - start[1]) == 1):
                                #check if black piece is there
                                #check if black piece present
                                let = end[0]
                                num = end[1] - 2
                                posData = let + num
                                if(csv_setup(find()) == 'pp'):
                                    return True
                                else:
                                    return False

                            else:
                                return False
                        else:
                            return False
                        #if pawn is on the row opposite to where it started, than, it can take if another pawn is diagonal
                        #taking
                        #check row
                        if(int(end[1])-int(start[1]) == 1):
                            #check column both polarity is checked
                            if(int(ord(end[0])-ord(start[0])) == 1):
                                #check piece
                                if('b' in csv_setup(find(end))):
                                    return True
                                else:
                                    return False
                        
                        #regular movement(compete)
                        if(int(end[1]) - int(start[1]) == 1):
                            #check for other piece
                            if('e' in csv_setup(find(end))):
                                return True
                            else:
                                return False      
                        else: 
                            return False
                        #change to other piece (leaving this for the end)


            
                    case 'b':
                        #regular movement
                        rowDiff = int(end[1])-int(start[1])
                        colDiff = int(ord(end[0])-ord(start[0]))
                        if rowDiff or colDiff != 0:
                            if (rowDiff/colDiff == 1):
                                return True
                        else: 
                            return False
                    case 'h':
                        #check if one dif is 2 and one is 1. I think this covers
                        rowDiff = int(abs(end[1])-int(start[1]))
                        colDiff = int(abs(ord(end[0])-ord(start[0])))
                        if sorted([abs(rowDiff), abs(colDiff)]) == [1, 2]:
                            #only check if piece is at the end
                            if is_piece(end) != 'e':
                                if is_piece(end)[0] != 'b':
                                    return False
                            return True
                        else:
                            return False
                        #regular movement
                    case 'k':
                        rowDiff = int(abs(end[1])-int(start[1]))
                        colDiff = int(abs(ord(end[0])-ord(start[0])))
                        if(colDiff + rowDiff == 1):
                            #check piece
                            if is_piece_interrupt(start, end) == True:
                                return False
                            return True

                        else:
                            return False
                        #regular movement
                    case 'q':
                        #regular movement
                        rowDiff = int(end[1])-int(start[1])
                        colDiff = int(ord(end[0])-ord(start[0]))

                        if rowDiff or colDiff != 0:
                            #moving diagonal
                            if (rowDiff/colDiff == 1):
                                if is_piece_interrupt == False:
                                    return True
                        else: 
                            #moving row or column
                            if (rowDiff or colDiff == 0) and (rowDiff or colDiff != 0):
                                if is_piece_interrupt == False:
                                    return True
                            return False
                        #regular movement
                    case 'c':
                        if (rowDiff or colDiff == 0) and (rowDiff or colDiff != 0):
                            if is_piece_interrupt == False:
                                return True
                            return False
                        return False

                        #this is left check 
                            #require king on spot. 
                            #require rook on spot
                            #require nothing in between
                            #require nothing looking at it
                            #require nothing moved
                        if csv_setup(find(start)) == "bk":
                            if csv_setup(find("a1")) == "bc":
                                if (is_piece_interrupt(start, end)):
                                    if fog_of_war(start, end):
                                        return True

                        #if start on right
                        #regular movement
            case 'b':

                match piece:
                    case 'p' | 'pp':
                        #2 out on start (black pawns start on row 7, move downward)
                            #if pawn is in starting position, end position can be 2 out
                        if(abs(int(end[1])-int(start[1])) == 2):
                            if(int(start[1]) == 7):
                                pos = csv_setup(find(end))
                                let = end[0]
                                num = end[1] + 1
                                pospre = let + num
                                pospreP = csv_setup(find(pospre))
                                if(pos == 'e' and pospreP == 'e'):
                                    return True
                                else:
                                    return False
                            else:
                                return False
                        else:
                            return False
                        #en passente
                            #if pawn is on the row opposite to where it started, than, it can take if another pawn is diagonal
                        if(int(start[1]) == 1) and (int(end[1]) ==2):
                            if(abs(ord(start[0]) - ord(end[0])) == 1):
                                let = end[0]
                                num = end[1] + 1
                                posData = let + num
                                if(csv_setup(find(posData)) == 'wp'):
                                    return True
                                else:
                                    return True
                            else:
                                return False
                        else:
                            return False
                        #taking diagonally
                        if(int(end[1]) - int(start[1]) == -1):
                            if(abs(int(ord(end[0]) - ord(start[0]))) == 1):
                                if('w' in csv_setup(find(End))):
                                    return True
                                else:
                                    return False
                        #regular movement
                        if (int(end[1]) - int(start[1]) == -1):
                            if(csv_setup(find(end)) == 'e'):
                                return True
                            else:
                                return False
                        else:
                            return False
            
                    case 'b':
                        #regular movement
                        rowDiff = int(end[1]) - int(start[1])
                        colDiff = int(ord(end[0]) - ord(start[0]))
                        if rowDiff or colDiff != 0:
                            if (rowDiff / colDiff == 1):
                                if is_piece_interrupt(start, end) == False:
                                    if not ('b' in csv_setup(find(end))):
                                        return True
                        return False
                    case 'h':
                        #regular movement
                        rowDiff = int(end[1]) - int(start[1])
                        colDiff = int(ord(end[0]) - ord(start[0]))
                        if sorted([abs(rowDiff), abs(colDiff)]) == [1, 2]:
                            if is_piece(end) != 'e':
                                if is_piece(end)[0] == 'b':
                                    return False

                            return True
                        else:
                            return False
                    case 'k':
                        #regular movement
                        rowDiff = int(end[1]) - int(start[1])
                        colDiff = int(ord(end[0]) - ord(start[0]))
                        if(colDiff + rowDiff == 1):
                            if is_piece_interrupt(start, end) == True:
                                return False
                            if 'b' in csv_setup(find(end)):
                                return False
                            return True
                        else:
                            return False
                    case 'q':
                        #regular movement
                        rowDiff = int(end[1]) - int(start[1])
                        colDiff = int(ord(end[0]) - ord(start[0]))
                        if rowDiff or colDiff != 0:
                            if (rowDiff / colDiff == 1):
                                if is_piece_interrupt(start, end) == False:
                                    if not ('b' in csv_setup(find(end))):
                                        return True
                            elif(rowDiff == 0) != (colDiff == 0):
                                if is_piece_interrupt(start, end) == False:
                                    if not ('b' in csv_setup(find(end))):
                                        return True
                        return False
                    case 'c':
            
                        #regular movement
                        rowDiff = int(end[1]) - int(start[1])
                        colDiff = int(ord(end[0]) - ord(start[0]))
                        if(rowDiff == 0) != (colDiff ==0):
                            if is_piece_interrupt(start, end) == False:
                                if not ('b' in csv_setup(find(end))):
                                    return True
                        return False
                        #if start on left
                        if csv_setup(find(start)) == 'bk':
                            if csv_setup(find("a8")) == "bc":
                                if not is_piece_interrupt(start, 'a8'):
                                    if not fog_of_war(start, end):
                                        return True
                        #if start on right
                        if csv_setup(find(start)) == 'bk':
                            if csv_setup(find("h8")) == "bc":
                                if not is_piece_interrupt(start, 'h8'):
                                    if not fog_of_war(start, end):
                                        return True
                       

    
    #tells us if a piece of the same side is present on end space
    def is_piece(end):
        return csv_setup(find(end))

    # tells us if any piece interrupts the start and end path of the two pieces
    def is_piece_interrupt(start, end):
        #pos ex a5
        #holds all information of spaces
        diffLetter = abs(ord(end[0]) - ord(start[0])) #int
        diffNum = abs(end[0] - start[0])
        alphabet = string.ascii_lowercase
        #we can leverage that piece either moves diagnol or horizontal 
        #fix stateent I cant figure out conditions exactly
        if(int(end[1])-int(start[1]) / int(ord(end[0])-ord(start[0])) == 1):
            for i in range(0, max(diffLetter, diffNum)):
                numP = diffNum + i
                pos = alphabet[diffLetter + i] + numP 
                posStr = csv_setup(find(pos))
                if posStr != 'e':
                    return False #basically checks all in range making sure it is 'e' for empty
        else:
            for i in range(0, max(diffLetter, diffNum)):
                #change row (num change)
                if end[0] != start[0]:
                    numP = diffNum + i
                    pos = alphabet[diffLetter] + numP 
                    posStr = csv_setup(find(pos))
                    if posStr != 'e':
                        return False
                #change column (num change)
                else:
                    pos = alphabet[diffLetter + 1] + diffNum
                    posStr = csv_setup(find(pos))
                    if posStr != 'e':
                        return False
        #there is no edge case here and the program assumes that you have a stage where edge of bad move has already been checked...
        return True


    def updateChess(side, piece, start, end):
        csv_setup(udpateCSV(piece, start, end))

    #a function to qualify if a piece can move in a certain spot everb
    def fog_of_war_side_specific(side, start, end):
        if side == 'b':
            side == 'w'
            pieceL= csv_setup(piecelist())
            fog = inBetween(start, end)
            for piece in pieceL:
                move_diary = allmove(csv_setup(find(piece)))
                if move_diary in fog:
                    return False
        else:
            side == "b"
            pieceL= csv_setup(piecelist())
            fog = inBetween(start, end)
            for piece in pieceL:
                move_diary = allmove(csv_setup(find(piece)))
                if move_diary in fog:
                    return False

        return True

    def inBetween(start, end):
        move = []
        rowDiff = int(end[1])-int(start[1])
        colDiff = int(ord(end[0])-ord(start[0]))
        #horizontal
        if (start[0] == end[0]):
            move.append(start)
            for i in range(0, colDiff):
                letter = alphabet[ord(start[0]) + i]
                num = str(int(start[1]))
                pos = letter + num
                move.append(pos)
            return move
        #vertical
        if (start[1] == end[1]):
            move.append(start)
            for i in range(0, rowDiff):
                letter = alphabet[ord(start[0])]
                num = str(i + int(start[1]))
                pos = letter + num
                move.append(pos)
            return move

        #diagonal
        if (rowDiff/colDiff == 1):
            move.append(start)
            ord(start[0])
            for i in range(0, rowDiff):
                letter = alphabet[ord(start[0]) + i]
                num = i + int(start[1])
                pos = letter + num
                move.append(pos)
            return move
        else:
            print("you are a silly goose and need to debug")
        
