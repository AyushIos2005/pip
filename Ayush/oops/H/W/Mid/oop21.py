class EmailValidator:
    def is_valid(self, email):
        at_pos = email.find('@')
        dot_pos = email.rfind('.')

        if at_pos <= 0:
            return False
        if dot_pos <= at_pos + 1:
            return False
        if dot_pos == len(email) - 1:
            return False
        if " " in email:
            return False

        return True


# Example usage
validator = EmailValidator()
email = input("Enter email: ")

if validator.is_valid(email):
    print("Valid Email")
else:
    print("Invalid Email")