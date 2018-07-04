#coding=utf-8
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from hashlib import sha1
from models import *


# 跳转到注册界面
def register(request):
    content = {"title":"天天生鲜－注册"}
    return render(request,"tt_user/register.html",content)


# 用户名预处理　是否注册过
def nameycl(request,name):
    num = UserInfo.objects.filter(uname=name).count()
    return JsonResponse({"data":num})


# 注册页提交用户数据
def register_cl(request):
    post = request.POST
    uname = post["user_name"]
    upwd = post["pwd"]
    upwd2 = post["cpwd"]
    uemail = post["email"]

    # 如果密码不相等　返回到注册页面　不需要
    # if upwd != upwd2:
    #     return redirect("/user/register")

    # 判空　不需要了
    # if uname == "" or upwd == "" or uemail == "":
    #     return redirect("/user/register")

    # 使用sha1加密
    s = sha1()
    s.update(upwd)
    upwd3 = s.hexdigest()

    # 创建数据库模型对象并写入
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    return redirect("/user/login")


# 跳转到登录界面
def login(request):
    cookie = request.COOKIES
    uname = ""
    if cookie.has_key("uname"):
        uname = cookie["uname"]
    content = {"title":"天天生鲜－登录","uname":uname}
    return render(request,"tt_user/login.html",content)
# placeholder="请输入用户名"


# 用户登录页密码对比
def pwd_cl(request):
    name = request.POST["name"]
    pwd = request.POST["pwd"]
    data = None
    try:
        user = UserInfo.objects.get(uname=name)
        pwd2 = user.upwd
        s = sha1()
        s.update(pwd)
        pwd3 = s.hexdigest()
        if pwd2 != pwd3:
            data = 0
        elif pwd2 == pwd3 and name == user.uname:
            data = 1
            # 保存登录信息到session
            request.session["user"] = name
            request.session.set_expiry(0)
    except Exception as e:
        print(e)
    return JsonResponse({'data':data})


# 用户登录时处理记住用户名
def cookie(request,name):
    response = HttpResponse()
    response.set_cookie("uname",name,max_age=1209600)
    return response


# 跳转到用户中心
def centerInfo(request):
    user = request.session.get("user",default=None)
    if user == None:
        return redirect("/user/login")
    else:
        user = UserInfo.objects.get(uname=user)
        content = {"title":"天天生鲜－用户中心","uname":user.uname,"uemail":user.uemail}
    return render(request,"tt_user/user_center_info.html",content)




def centerSite(request):
    user = request.session.get("user",default=None)
    if user == None:
        content = {"title":"天天生鲜－用户中心","addr":""}
    else:
        user = UserInfo.objects.get(uname = user)
        content = {"title":"天天生鲜－用户中心","addr":user.uadder,"name":user.ushou,"tel":user.utel}
    return render(request,"tt_user/user_center_site.html",content)

def centerSite_cl(request):
    user = request.session.get("user", default=None)
    if user == None:
        pass
    else:
        newuser = UserInfo.objects.get(uname=user)
        print(type(newuser))
        newuser.uadder = request.POST["uaddr"]
        newuser.ushou = request.POST["uname"]
        newuser.uyoubian = request.POST["uyoub"]
        newuser.utel = request.POST["utel"]
        print(newuser.uname)
        print(newuser.uadder+newuser.ushou+newuser.uyoubian+newuser.utel)
        newuser.save()
    return redirect("/user/centersite")

def centerOrder(request):
    return render(request,"tt_user/user_center_order.html")