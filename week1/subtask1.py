# Create a program that will ask the user for two numbers and then 
# show the sum, product, ratio, modulus and exponentiation.

a = int(input("Enter a frist number: "))
b = int(input("Enter a second number: "))

sum = a + b
product = a * b
ratio = a / b
modulus = a % b
exponentiation = a ** b

a = str(a)
b = str(b)

print("Sum of " + a + " and " + b + ": " + str(sum))
print("Product of " + a + " and " + b + ": " + str(product))
print("Ratio of " + a + " and " + b + ": " + str(ratio))
print("Modulus of " + a + " and " + b + ": " + str(modulus))
print("Exponentiation of " + a + " and " + b + ": " + str(exponentiation))

