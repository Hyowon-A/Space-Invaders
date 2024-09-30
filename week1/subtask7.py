# Create a program that asks the user for their age, 
# the program should output false if the person is less than 18 years old 
# and true if the person is greater than 17 years old (do use a conditional if statement).

age = int(input("Enter your age: "))

if age < 18:
  print(False)
else: 
  print(True)