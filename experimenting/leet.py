# if str(x) == str(x)[::-1]:
#     return True
# return False

x = 121

# if x < 0:
#     return False

# print(int(7 / 10))

y = x
digits = 0
while y != 0:
    y = int(y / 10)
    digits += 1

z = 0
lastD = 0

for i in range(digits):
    a = int(x / (10 ** (digits - i - 1)))
    b = a * (10 ** i) - lastD
    z += b
    lastD = int(x / (10 ** (digits - i - 1))) * (10 ** (digits - i - 1))

print(z)