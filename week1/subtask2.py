# Create a program that asks the user for a temperature in degrees Celsius 
# and display the conversion in Fahrenheit.

celsius = float(input("Enter a temperature in degree Celsius: "))

fahrenheit = celsius * 9/5 + 32

print("The temperature in Fahrenheit is " + str(fahrenheit))
