from openai import OpenAI
import json
from gpt_functions import gpt_functions

class session:
    # 세션은 파일에 저장되며, 챗로그+파일명+모델로 구성됨  
    def __init__(self,current_filename):
        with open("openai_api.key") as f:
            key=f.read() # TODO : env로 바꾸기
        self.client = OpenAI(api_key=key)
        self.model="gpt-4o"
        self.current_filename:str=current_filename
        self.chatlog=[]
        self.gpt_function=gpt_functions(self)
        self.gpt_func:(list | None)=[] #빈 리스트를 그대로 사용하면 오류 발생
        self.load_functions()
        self.load_session()
     
    def load_session(self):
        # 파일에서 세션 불러오기
        try:
            with open(self.current_filename,"r",encoding="utf-8") as f:
                history=f.read()
            self.chatlog:list=json.loads(history)
        except FileNotFoundError:
            # 파일이 없으면 새로운 파일 생성
            with open(self.current_filename,"w") as f:
                pass
            self.chatlog=[]
        except json.JSONDecodeError:
            # 파일이 깨졌으면 오류처리, 공란인 경우 새로 작성
            if history:
                raise Exception("File corruption detected")
            self.chatlog=[]
        except Exception as e:
            raise Exception("Unknown Error", e)
        
        if not isinstance(self.chatlog,list):
            # 임의로 list 형식을 벗어난 json 감지
            raise Exception("File corruption detected")
        
        for message in self.chatlog:
            try:
                print(f"{message['role']} : {message['content']}")
            except KeyError:
                raise Exception("File corruption detected")
        
    def save_session(self,_indent=4):
        # json으로 세션(대화기록) 내보내기
        with open(self.current_filename,"w",encoding="utf-8") as f:
            f.write(json.dumps(self.chatlog,ensure_ascii = False,indent=_indent))
        
    def change_model(self):
        # 모델 바꾸기
        model_list=["gpt-4o","gpt-4o-mini","o1-mini","o1-preview"]
        print(f"Current : {self.model}")
        for i in range(len(model_list)):
            print(f"[{i}] {model_list[i]}")
        while True:
            choice=int(input("> "))
            if 0<=choice<len(model_list):
                self.model=model_list[choice]
                break
            else:
                print("잘못된 선택입니다.")
            
    def change_session(self):
        self.current_filename=input("Enter new session name> ")
        self.load_session()

    def append_chat(self,role:str,content:str,func_name=None):
        # 세션에 대화 붙이기
        if not content:
            raise "내용이 비어있습니다."
        message={"role":role,"content":content}
        if func_name:
            message["name"]=func_name
        self.chatlog.append(message)

    def gptchat(self,user_input:str):
        def check_functioncall(response,max_repeat=5):
            #함수 호출이 감지되면 실행 후 다시 대화생성
            for repeat in range(max_repeat):
                if (response.choices[0].finish_reason == "function_call"):
                    func=response.choices[0].message.function_call
                    function_ret:str=self.gpt_function(func.name)(**json.loads(func.arguments))
                    self.append_chat("function",function_ret,func.name)
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.chatlog,
                        functions=self.gpt_func if function_ret!="reject" else None 
                        #TODO : 문자열을 비교하는건 우아하지 못한거같네요. Exception으로 처리하는게 낫겠어요
                    )
                else:
                    break
            return response
        
        self.append_chat("user",user_input)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.chatlog,
            functions=self.gpt_func
        )
        response=check_functioncall(response)
        
        answer=response.choices[0].message.content
        self.append_chat("assistant",answer)
        print(f"assistant({self.model}) : {answer}")
        self.save_session()
    
    def setting(self):
        #TODO : 채팅내역삭제 등 -> 중요성 낮은듯
        print("[0] Change Model")
        print("[1] Change Session")

        choice=input("> ")
        if choice=="0":
            self.change_model()
        elif choice=="1":
            self.change_session()
            
    def load_functions(self):
        def class_into_list(c):
            ret = []
            for item in dir(c):
                if not(item.startswith("__") or item.endswith("__")):
                    if callable(func:=getattr(c,item)):
                        ret.append(func) 
            return ret
        funcs:list=class_into_list(self.gpt_function)
        for func in funcs:
            self.gpt_func.append(json.loads(func.__doc__))
        #비어있는 리스트 사용시 오류 발생하므로 None으로 초기화해줌
        if not(self.gpt_func):
            self.gpt_func=None