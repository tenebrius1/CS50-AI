from nim import train, play
import time

start = time.time()
ai = train(10000)
print(f"---  {time.time() - start}  ---")
play(ai)

while True:
    play_again = input("Do you want to play again? y/n \n")
    if play_again == "y":
        play(ai)
    else:
        break
