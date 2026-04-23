import csv
import shutil


class csv_setup():

    RESET_FILEPATH = r"data\chess_reset.csv"
    GAME_FILEPATH  = r"data\chess_document.csv"

    @staticmethod
    def setup():
        # Just copy the reset file into the working game file
        shutil.copyfile(csv_setup.RESET_FILEPATH, csv_setup.GAME_FILEPATH)


    @staticmethod
    def findSpaceofPiece(piece):
        #this will search through the entire csv rapidly and find the sapce of a given piece
        
        #col = ord(pos[0].lower() - ord('a'))
        #row = int(pos[1])
        return reader[row][col]
    
    @staticmethod
    def findPiecewithSpace(space):
        #this will search through the csv rapidly and give us the piece fro the start and end
        return 'k'

    @staticmethod #registers piece movement
    def updateCSV(piece, start, end):
        col_s = ord(start[0].lower()) - 1
        row_s = int(start[1]) - 1
        col_e = ord(end[0].lower()) - 1
        row_e = int(end[1]) - 1

        with open(csv_setup.GAME_FILEPATH, 'r') as f:
            board = list(csv.reader(f))
        board[row_e][col_e] = piece
        board[row_s][col_s] = 'e'
        with open(csv_setup.GAME_FILEPATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(board)

    #return a list of pieces in the csv
    def piecelist():
        with open(csv_setup.GAME_FILEPATH, 'r') as f:
            board = list(csv.reader(f))
        return [cell for row in board for cell in row if cell != 'e']