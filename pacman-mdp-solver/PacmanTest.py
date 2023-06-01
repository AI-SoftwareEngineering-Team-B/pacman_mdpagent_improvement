# pacmanTest.py
# 21-05-2023 / jjm
#
# This file is created to easily test the changed code. 
#
import subprocess

def get_score_and_win(output):
    lines = output.split('\n')
    score = None
    win = None
    for line in lines:
        if "Score: " in line:
            # Convert to float first, then to int
            score = int(float(line.split("Score: ")[1]))
        if "Record: " in line:
            win = "Win" in line.split("Record: ")[1]
    return score, win

# Change the command as needed and use it.
# --frameTime (speed): Change the speed of game progress. default is 0.1
# -t : Disable graphics and play the game over text
# -q : Turn graphics off and play the game
command = ["python2", "pacman.py", "-p", "MDPAgent", "--frameTime", "0.01", "-q"]
# how many times to try
runs = 10
scores = []
wins = 0
errors = 0

for i in range(runs):
    result = subprocess.run(command, stdout=subprocess.PIPE)
    score, win = get_score_and_win(result.stdout.decode('utf-8'))
    if score is not None:
        scores.append(score)
    else:
        print('An Error Occured')
        scores.append(0)
        errors += 1
    if win:
        wins += 1

    print("try : ", i+1, " | score : ", scores[i], " | win : ", win)

average_score = sum(scores) / len(scores) if scores else 0

print("Scores: ", scores)
print("Average Score: ", average_score)
print("Total Wins: ", wins)
print("Errors : ", errors)