def update_unread(messages):
    for message in messages:
        message.change_unread()
        message.save()
        
    
def update_list_unread(messages):
    for message in messages:
        message["unread"]= False
    
