class gpt_functions:
    def __init__(self,s):
        self.session=s
    
    def __call__(self,name):
        if hasattr(self,name):
            return getattr(self,name)
        raise Exception(f"존재하지 않는 함수({name})를 참조했습니다.")
    
    @staticmethod
    def time_check():
        """
        {
            "name" : "time_check",
            "description" : "현재 시간을 불러오는 함수",
            "parameters" : {
                "type" : "object",
                "properties" : {
                }
            },
            "required":[]
        }
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d - %H:%M:%S")
    
    def cmd(self,command):
        """
        {
            "name" : "cmd",
            "description" : "윈도우를 사용하는 사용자의 cmd 명령어를 제한적으로 사용합니다. 사용자의 최종 확인이 있어야합니다.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "command" : {
                        "type" : "string",
                        "description" : "cmd로 실행할 명령어"
                    }
                }
            },
            "required":["command"]
        }
        """
        import os
        print(f"경고 : chatgpt가 ({command})를 실행하려합니다. 계속 진행하시겠습니까?(y/n)")
        if input().lower()!="y":
            self.session.append_chat("system","사용자가 명령어를 거부하였습니다.")
            return "reject"
        else:
            try:
                shell=os.popen(command)
                result=shell.read()
                shell.close()
                self.session.append_chat("system","assistant는 함수를 그만 호출해도됩니다.")
                if result:
                    print(f"system : {result}")
                else:
                    result="명령을 성공적으로 수행했습니다."
                return result
            except Exception as e:
                self.session.append_chat("system",f"명령 수행중 에러가 발생했습니다. {e}")
                return "error"