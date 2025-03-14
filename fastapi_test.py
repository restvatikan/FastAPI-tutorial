from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# 전역 딕셔너리: key는 회원 id, value는 회원 pw (암호화 없이 평문 저장)
users = {}

# -------------------------------
# 홈 페이지: 로그인 상태에 따라 우측 상단에 user_id 및 로그아웃 링크 표시
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # 요청 쿠키에서 로그인한 user_id를 조회 (없으면 None)
    login_user = request.cookies.get("user_id")
    
    # 로그인 되었을 경우 우측 상단에 사용자 정보와 로그아웃 링크 삽입
    user_info_html = ""
    if login_user:
        user_info_html = f"""
            <div style="position: absolute; top: 10px; right: 10px;">
                <strong>{login_user}</strong> 님 로그인 중 |
                <a href="/logout">로그아웃</a>
            </div>
        """
    
    html_content = f"""
    <html>
        <head>
            <title>Member Portal</title>
        </head>
        <body>
            {user_info_html}
            <h1>환영합니다!</h1>
            <ul>
                <li><a href="/register">회원 가입</a></li>
                <li><a href="/login">로그인</a></li>
                <li><a href="/users">회원 목록 조회</a></li>
            </ul>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# -------------------------------
# 회원가입 폼 제공 (GET /register)
# -------------------------------
@app.get("/register", response_class=HTMLResponse)
def register_form():
    html_content = """
    <html>
        <head>
            <title>User Registration</title>
        </head>
        <body>
            <h2>회원 가입</h2>
            <form action="/register" method="post">
                <label for="user_id">User ID:</label>
                <input type="text" id="user_id" name="user_id" required><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required><br>
                <input type="submit" value="가입하기">
            </form>
            <br>
            <a href="/">홈 화면으로 이동</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# -------------------------------
# 회원가입 처리 (POST /register)
# -------------------------------
@app.post("/register")
def register(user_id: str = Form(...), password: str = Form(...)):
    # 이미 존재하는 회원이면 에러 발생
    if user_id in users:
        return HTMLResponse(content=f"""
            <script>
                alert("이미 가입한 사용자입니다.");
                window.location.href="/register";
            </script>
        """)
    users[user_id] = password   # 평문으로 저장 (실제 서비스에서는 해시 처리가 필요)
    # 회원가입 후 로그인 페이지로 리다이렉트
    return RedirectResponse(url="/login", status_code=303)

# -------------------------------
# 로그인 폼 제공 (GET /login)
# -------------------------------
@app.get("/login", response_class=HTMLResponse)
def login_form():
    html_content = """
    <html>
        <head>
            <title>User Login</title>
        </head>
        <body>
            <h2>로그인</h2>
            <form action="/login" method="post">
                <label for="user_id">User ID:</label>
                <input type="text" id="user_id" name="user_id" required><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required><br>
                <input type="submit" value="로그인">
            </form>
            <br>
            <a href="/">홈 화면으로 이동</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# -------------------------------
# 로그인 처리 (POST /login)
# 2) 아이디가 없으면 "존재하지 않는 회원입니다." 팝업,
# 3) 아이디는 있으나 비번이 틀리면 "비밀번호가 틀립니다." 팝업,
# 4) 로그인 성공 시 "{user_id}님, 환영합니다." 팝업 및 쿠키에 user_id 저장
# -------------------------------
@app.post("/login")
def login(user_id: str = Form(...), password: str = Form(...)):
    if user_id not in users:
        # 아이디가 존재하지 않음 → JS alert 후 로그인 페이지로 이동
        return HTMLResponse(content="""
            <script>
                alert("존재하지 않는 회원입니다.");
                window.location.href="/login";
            </script>
        """)
    elif users[user_id] != password:
        # 아이디는 있으나 비밀번호가 틀림 → JS alert 후 로그인 페이지로 이동
        return HTMLResponse(content="""
            <script>
                alert("비밀번호가 틀립니다.");
                window.location.href="/login";
            </script>
        """)
    # 로그인 성공: JS alert 후 홈으로 이동, 쿠키에 user_id 저장
    html_content = f"""
    <html>
        <head>
            <title>Login Successful</title>
        </head>
        <body>
            <script>
                alert("{user_id}님, 환영합니다.");
                window.location.href="/";
            </script>
        </body>
    </html>
    """
    response = HTMLResponse(content=html_content)
    # 쿠키에 user_id를 저장하여 홈 화면에 표시(쿠키 유효범위: 전체 경로)
    response.set_cookie(key="user_id", value=user_id, path="/")
    return response

# -------------------------------
# 로그아웃 처리 (GET /logout)
# 로그인 쿠키를 삭제하고 홈으로 이동하는 팝업 제공
# -------------------------------
@app.get("/logout", response_class=HTMLResponse)
def logout():
    response = HTMLResponse(content="""
        <script>
            alert("로그아웃 되었습니다.");
            window.location.href="/";
        </script>
    """)
    response.delete_cookie(key="user_id")
    return response

# -------------------------------
# 회원 목록 조회 (GET /users)
# 1) 각 회원 옆에 삭제 기능을 추가한 페이지
# -------------------------------
@app.get("/users", response_class=HTMLResponse)
def user_list():
    user_items = ""
    for user in users.keys():
        # 각 회원 아이디 옆에 '삭제' 링크 추가 (클릭 시 삭제 확인 메시지)
        user_items += f"<li>{user} - <a href='/delete_user?user_id={user}' onclick='return confirm(\"삭제하시겠습니까?\");'>삭제</a></li>"
    html_content = f"""
    <html>
        <head>
            <title>Member List</title>
        </head>
        <body>
            <h2>회원 목록 조회</h2>
            <ul>
                {user_items}
            </ul>
            <br>
            <a href="/">홈 화면으로 이동</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# -------------------------------
# 회원 삭제 처리 (GET /delete_user)
# 요청 쿼리 스트링으로 전달된 user_id를 삭제 후 회원 목록 페이지로 리다이렉트
# -------------------------------
@app.get("/delete_user", response_class=HTMLResponse)
def delete_user(user_id: str):
    if user_id in users:
        del users[user_id]
    return RedirectResponse(url="/users", status_code=303)

# -------------------------------
# 앱 실행: 이 파일이 직접 실행될 때 uvicorn으로 서버 실행
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
