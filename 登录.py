from cqrk.user import user
from cqrk.jwxt import jwxt

username = '学号'
password = '密码'

User = user(username,password)
Jwxt = jwxt(User.loadCookie())

if not User.isCookieEnable():
    if User.login():
        print('登录成功')

studentInfo = Jwxt.getStudentInfo()
print(f"你好，{studentInfo['name']}。")