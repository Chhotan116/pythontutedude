
'''print("hello everyone! We are learning python.")
num =10
print(num)'''

'''age=int(input("What's your age? "))
name=input("what is your name? ")
print(name,age)'''

#print(max(1,2,3,4,5,6))
#pri nt(min(1,2,3,4,5,6))
#print9abs(-2020))
#print(pow(2,3))
#print(min(1,2,3,4,5,6,7,8,9))
#a=1,2,3,4,5,6,7,8,9,10'''
# when all the length of the sides of the triangle is known as- a,b,c
#semi perimeter(s)=(a+b+c)/2
#area=square root of (s*(s-a)*(s-b)*(s-c)) a= float(input("Enter first side: "))
'''a=float(input("Enter first side: "))
b = float(input("Enter second side: "))
c = float(input("Enter third side: "))
s = (a + b + c) / 2
area = (s * (s - a) * (s - b) * (s - c)) ** 0.5
print("area of triangle with given side is", area)'''
#simple interest = (p*R*T)/100
#p= principal amount
#R= rate of interest
#T= time
'''p=int(input("Enter a principal amount(p): "))
r=float(input("Enter rate of interest(in %): "))
t=int(input("Enter time duration for the interest(t): "))
simple_interest=(p*r*t)/100
print("Simple interest is", simple_interest)'''

#compound interest (A)= p(1+r/n)**t
#p= principal amount
#R= rate of interest
#T= time
# Compound Interest Calculator

'''P = float(input("Enter Principal Amount: "))
R = float(input("Enter Rate of Interest (in %): "))
T = float(input("Enter Time (in years): "))'''

# Compound Interest Formula
'''A = P * (1 + R/100) ** T   # Final amount
CI = A - P                 # Compound Interest

print("Total Amount =", round(A, 2))
print("Compound Interest =", round(CI, 2))'''
#area of right angle triangle
'''b=float(input("Enter the base: "))
p=float(input("Enter the height: "))
A= 1/2*b*p #area of right angle triangle
print("area of right angle triangle with given side is",A)'''

#how to find the triplet

b=int(input("Enter the base(b): "))
p=int(input("Enter the height(p): "))
h=int(b**2+p**2)**(1/2)
print("h=",round(h,2))
if h**2==p**2+b**2:
    print("It is a right angle triangle")
else:
    print("It is Not a right angle triangle")
git config --global user.name "Chhotan116"