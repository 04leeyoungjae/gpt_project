from openai import OpenAI
import json
key=open("openai_api.key").read() # TODO : env로 바꾸기
client = OpenAI(api_key=key)

def load_history(filename="chat.json"):
    # TODO : session class에 두개다 넣기
    current_session=json.loads(open(filename,"r",encoding="utf-8").read())
    current_filename=filename
    
    for message in current_session:
        print(f"{message['role']} : {message['content']}")
    return current_session,current_filename

def save_session(current_session):
    open("chat.json","w",encoding="utf-8").write(json.dumps(current_session,ensure_ascii = False))

def make_message(current_session,role,content):
    current_session.append({"role":role,"content":content})

def chat(current_session):
    user_input=input("user : ")
    if user_input=="/set":
        #TODO : 모델변경, 세션바꾸기, 채팅바꾸기 등
        print("미구현")
    else:
        gptchat(current_session,user_input)

def gptchat(current_session,user_input):    
    make_message(current_session,"user",user_input)
    response = client.chat.completions.create(
        model="o1-mini",
        messages=current_session
    )
    answer=response.choices[0].message.content
    make_message(current_session,"assistant",answer)
    print(f"assistant : {answer}")
    save_session(current_session)
     
if __name__=="__main__":
    current_session,current_filename = load_history()
    chat(current_session)