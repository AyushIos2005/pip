import smtplib as stp 

object = stp.SMTP('smtp.gmail.com',587)
object.ehlo()
object.starttls()


object.login("ayushverma8605@gmail.com","yqsf dvuw zgla wyno")

subject="Testing"
body="I love py"
message="subject:{}\n\n{}".format(subject,body)

li=['prajapatgaurav08@gmail.com','ayushvermacseds@gmail.com']

object.sendmail('ayushverma8605@gmail.com',li,message)
print("Sended Mail")
object.quit()




# Ayush@212169