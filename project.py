from session import session
    
def chat(current_session:session):
    print(f"디버그 : {current_session.current_filename, current_session.model}")
    user_input=input("user : ")
    if user_input=="/exit":
        exit(0)
    if user_input=="/set":
        current_session.setting()
    else:
        current_session.gptchat(user_input)
     
if __name__=="__main__":
    current_session = session("chat.json")
    while True:
        chat(current_session)