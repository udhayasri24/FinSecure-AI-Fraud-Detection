import smtplib

def send_email_alert(prob):
    sender = "your_email@gmail.com"
    password = "your_app_password"
    receiver = "receiver@gmail.com"

    msg = f"Subject: Fraud Alert 🚨\n\nFraud probability: {prob}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg)
        server.quit()
    except:
        pass