import os 
dirs = os.listdir('nord_vpn')

for vpn in dirs:
    with open(os.path.join('nord_vpn', vpn), 'r', encoding='utf-8') as fl:
        text = fl.read()
    index = text.find('auth-user-pass') + 14
    text = text[:index] + ' cfg' + text[index:]
    with open(os.path.join('nord_vpn', vpn), 'w', encoding='utf-8') as fl:
        fl.write(text)
