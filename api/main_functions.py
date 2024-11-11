from django.core.mail import EmailMultiAlternatives





def SendEmail(email, subject, message):
    subject = subject
    # message = '<h1>This email was sent from django</h1>'
    from_email = 'akshatnigamcfl@gmail.com'
    recipient_list = email
    text = 'email sent from MyDjango'
    email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
    email.attach_alternative(message, 'text/html')
    # email.attach_file('files/uploadFile_0dTGU7A.csv', 'text/csv')
    email.send()
