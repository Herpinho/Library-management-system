import sys
CMD_WIDTH = 232
import json
def chat_bubble(message, align="left"):

    big_line = 0
    message = str(message)
    lines = message.strip().split('\n')
    for line in lines:
        if len(line) > big_line or big_line == 0:
            big_line = len(line)
    box_bottop = '─' * (big_line+2)
 
    if align == "right":
        print(f"┌{box_bottop}┐".rjust(CMD_WIDTH))
        for line in lines:
            formated_text = line.rjust(big_line)
            print(f"│ {formated_text} │".rjust(CMD_WIDTH))
        print(f"└{box_bottop}┘".rjust(CMD_WIDTH))
    else:
        print(f"┌{box_bottop}┐")
        for line in lines:
            formated_text = line.ljust(big_line)
            print(f"│ {formated_text} │")
        print(f"└{box_bottop}┘")
def title(title):
    width = len(title)
    bottop = '═' * (width + 2)
    print(f"╔{bottop}╗".center(CMD_WIDTH))
    print(f"║ {title} ║".center(CMD_WIDTH))
    print(f"╚{bottop}╝".center(CMD_WIDTH))
def user_input():
    user_input = input("\n > ")
    sys.stdout.write("\033[F\033[K")
    sys.stdout.flush()
    return user_input
def message_formatter(response):
    data = response.json()

    for key,value in data.items():
        if key in ['message','error']:
            return str(f"""
                        {key.capitalize()}
        {value}                            
        """)

    
def json_formatter(response):
    data = response.json()
    formatted_message = ""
    for key, value in data.items():
        if key.lower() != 'password':
            formatted_message +=f"{key.capitalize()}: {value}\n"
    return formatted_message
