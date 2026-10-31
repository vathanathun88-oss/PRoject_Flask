from gtts import gTTS
# def speak():
#     text="ចូលបានជោគជ័យ"
#     tts=gTTS(text=text, lang='km')
#     tts.save("voice.mp3")
#     print("Successfully")
# speak()

def speak1():
    text="ខុសពាក្យសម្ងាត់ហើយ​ បងប្រុស​ សូមសាកល្បងម្ដងទៀត​ សូមអរគុណ"
    tts=gTTS(text=text, lang="km")
    tts.save("static/worng_login.mp3")
    print("Ok")

def speak4():
    text="បង់ប្រាក់បានជោគជ័យ"
    tts=gTTS(text=text, lang="km")
    tts.save("static/succes.mp3")

def speak2():
    text="បងប្រុស ចូល​ បានជោគជ័យហើយ សូមអរគុណ!"
    tts=gTTS(text=text, lang="km")
    tts.save("static/loginice.mp3")
    print("Ok2")

def speak3():
    text="ចុះឈ្មោះបានជោគជ័យ"
    tts=gTTS(text=text, lang="km")
    tts.save("static/register.mp3")



