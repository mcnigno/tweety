mail = 'Danilo Pacifico <danilo.pacifico@gmail.com>'
mail2 = '<danilo.pacifico@gmail.com>'

def find_user_by_mail(recipients):
    try:
        last_word = recipients.split(' ')[-1]
    except:
        last_word = recipients
    
    if last_word[0] == '<':
        email_addr = last_word[1:-1]
    else:
        email_addr = last_word
    print(email_addr)

find_user_by_mail(mail2)