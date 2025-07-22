# Create the function
def check_string(s):
    if s.startswith("The"):
        return "Found it!"
    else:
        return "Nope."

# Test cases
str1 = 'The'
str2 = 'Thumbs up'
str3 = 'Theatre can be boring'

print(check_string(str1))    # ➜ Found it!
print(check_string(str2))    # ➜ Nope.
print(check_string(str3))    # ➜ Found it!
