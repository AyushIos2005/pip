# Take score and print performance message.
score = float(input("Enter the score (0-100): "))

if score >= 90:
    print("Performance: Excellent! 🌟")
elif score >= 80:
    print("Performance: Very Good! 👍")
elif score >= 70:
    print("Performance: Good. 😊")
elif score >= 60:
    print("Performance: Average. 😐")
elif score >= 0:
    print("Performance: Poor. Needs improvement. 📚")
else:
    print("Invalid score. Please enter a value between 0 and 100.")
