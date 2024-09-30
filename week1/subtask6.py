# Create a program that asks the user for their first name and then their surname. 
# The program should then display the person’s initials.

fName = input("Enter your frist name: ")
sName = input("Enter your surname: ")

print("Your initials: " + fName[0].upper() + ". " + sName[0].upper() + ".")