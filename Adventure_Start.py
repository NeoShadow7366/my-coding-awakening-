# Zelda-inspired adventure starter
print("You awaken in a dark cave... It's dangerous to go alone!")

weapon = input("What item do you pick up? (sword, boomerang, nothing): ").lower().strip()

if weapon == "sword":
    print("You grab the Master Sword! The blade hums with power. 🗡️")
    print("A voice echoes: 'Courage... Link... you must save Hyrule!'")
elif weapon == "boomerang":
    print("You snag the Boomerang! It spins back to your hand with a satisfying whoosh. 🪃")
    print("Now you can stun distant foes... or just annoy chickens.")
elif weapon == "nothing":
    print("You bravely choose... nothing. The old man sighs. 'Take this anyway, kid.'")
    print("He hands you a rusty sword anyway. Classic.")
else:
    print(f"You pick up a mysterious {weapon}... Wait, that's not canon! The cave rumbles.")
    print("Game over? Nah — adventure continues anyway. Improvise!")

print("\nYour journey begins. What will you do next?")