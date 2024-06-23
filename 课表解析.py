from tabulate import tabulate
from cqrk.jwxt import jwxt
from cqrk.user import user

username = '学号'

User = user()

if not User.login(user=username) : exit()

Jwxt = jwxt(User.loadCookie())
courseSheet = Jwxt.getCourseSheet(parse=True,onlyName=True)

# 定义表头
headers = ['周一', '周二', '周三','周四','周五','周六','周日']
data = [*zip(*courseSheet)]

# 使用tabulate生成表格
table = tabulate(data, headers=headers, tablefmt='grid')

# 输出表格
print(table)
