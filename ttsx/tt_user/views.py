#coding=utf-8
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from django.core.paginator import Paginator
from hashlib import sha1
from models import *
from tt_goods.models import *
from tt_order.models import *
import redis,base64,user_decorator


# 用户名预处理　是否注册过
def nameycl(request,name):
    num = UserInfo.objects.filter(uname=name).count()
    return JsonResponse({"data":num})


# 注册页提交用户数据
def register(request):
    if request.method == "GET":
        context = {"title": "天天生鲜－注册"}
        return render(request, "tt_user/register.html", context)
    else:
        post = request.POST
        uname = post["user_name"]
        upwd = post["pwd"]
        upwd2 = post["cpwd"]
        uemail = post["email"]
        count = UserInfo.objects.filter(uname=uname).count()
        if count != 0 or upwd != upwd2 or uname == "" or upwd == "" or upwd2 == "" or uemail == "":
            context = {"title": "天天生鲜－注册",}
            return render(request,"tt_user/register.html",context)
        else:
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
    user = request.session.get('user', default=None)
    cookie = request.COOKIES
    # 判断用户是否已经登录
    if user != None:
        url = cookie.get("url","/")
        rspred = HttpResponseRedirect(url)
        # 如果用户有储存url 则注销url的cookie
        if cookie.has_key("url"):
            rspred.set_cookie("url","",max_age=-1)
        return rspred
    # 判断用户本地cookie是否有用户名信息
    uname = ""
    if cookie.has_key("uname"):
        uname = cookie["uname"]
    content = {"title":"天天生鲜－登录","uname":uname}
    return render(request,"tt_user/login.html",content)


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
            request.session['user'] = name
            request.session.set_expiry(0)
    except Exception as e:
        print(e)
    return JsonResponse({'data':data})


# 用户登录时处理记住用户名
def cookie(request,name):
    response = HttpResponse()
    if name != "":
        response.set_cookie("uname",name,max_age=1209600)
    else:
        response.set_cookie("uname",name, max_age=-1)
    return response


# 跳转到用户中心 个人信息 装饰器为登录验证
@user_decorator.login
def centerInfo(request):
    user = request.session.get('user',default=None)
    content = {}
    user = UserInfo.objects.get(uname=user)
    content["title"] = "天天生鲜－用户中心"
    content["user"] = user
    content['active'] = 1
    cookie = request.COOKIES.get("liulan",None) # 接收cookie中的最近浏览信息
    liulanlist = []
    if cookie != None:
        liulan = cookie.split("-")              # 分割字符串、返回列表
        for i in liulan:
            goods = Goods.objects.get(id=i)     # 拿到id对应的商品并构成列表返回
            liulanlist.append(goods)
    content["liulan"] = liulanlist
    return render(request,"tt_user/user_center_info.html",content)


# 跳转到用户中心　收货地址 装饰器为登录验证
@user_decorator.login
def centerSite(request):
    user = request.session.get("user",default=None)
    content = {}
    # 如果是get提交、是来获取信息的
    if request.method == 'GET':
        user = UserInfo.objects.get(uname = user)
        content["title"] = "天天生鲜－用户中心"
        content["user"] = user
        content['active'] = 3
        return render(request,"tt_user/user_center_site.html",content)
    # 如果是POST提交、是来修改信息的
    else:
        newuser = UserInfo.objects.get(uname=user)
        newuser.uadder = request.POST["uaddr"]
        newuser.ushou = request.POST["uname"]
        newuser.uyoubian = request.POST["uyoub"]
        newuser.utel = request.POST["utel"]
        newuser.save()
        return redirect("/user/centersite")


# 跳转到用户中心　全部订单 装饰器为登录验证
@user_decorator.login
def centerOrder(request,id):
    print(id)
    user = request.session.get("user", default=None)
    content = {}
    user = UserInfo.objects.get(uname = user)
    content['user'] = user
    content["title"] = "天天生鲜－用户中心"
    content['active'] = 2
    content["order"] = None
    try: # 拿到用户的订单　分页返回
        order = OrderInfo.objects.filter(ouser=user)
        paginator = Paginator(order,2)
        if id == "":
            id = 1
        page = paginator.page(int(id))
        content["order"] = page
    except Exception as e:
        print(e)
    return render(request,"tt_user/user_center_order.html",content)


# 注销登录
def zhuxiao(request):
    user = request.session.get("user", default=None)
    re = redis.StrictRedis()
    rekey = re.keys()
    for i in rekey:
        try:
            jm = base64.b64decode(re.get(i))
            newjm = jm[41:]
            jm = eval(newjm)
            if jm["user"] == user:
                re.delete(i)
        except:
            continue
    return redirect("/")
