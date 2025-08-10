<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>	
<html>
<head>
	<meta charset="UTF-8">
	<title>로그인</title>
	<style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f8;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .loginBox {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
            width: 320px;
        }
        .loginBox h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        .loginBox label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
            font-size: 14px;
        }
        .loginBox input[type="text"],
        .loginBox input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 14px;
        }
        .loginBox button {
            width: 100%;
            padding: 10px;
            margin-top: 20px;
            background: #2196F3;
            border: none;
            color: white;
            font-size: 15px;
            border-radius: 6px;
            cursor: pointer;
        }
        .loginBox button:hover {
            background: #1976D2;
        }
        .error-message {
            color: red;
            text-align: center;
            margin-bottom: 10px;
        }
	</style>
</head>
</html>
<div class="loginBox">
    <h2>로그인</h2>

    <!-- 로그인 실패 시 메시지 출력 -->
    <c:if test="${not empty error}">
        <p style="color: red;">${error}</p>
    </c:if>

    <form action="${pageContext.request.contextPath}/login/loginProc.do" method="post">
        <label for="memId">아이디:</label>
        <!-- <input type="text" id="memId" name="memId" required /><br><br> -->
		<input type="text" name="memId" value="${lastLoginId}" placeholder="아이디"><br><br>
        <label for="memPw">비밀번호:</label>
        <input type="password" id="memPw" name="memPw" required /><br><br>

        <button type="submit">로그인</button>
    </form>
</div>



