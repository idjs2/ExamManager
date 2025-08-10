<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<<<<<<< HEAD
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
=======
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<style>
    /* 모달 기본 스타일 */
    .modal {
        display: none;
        position: fixed;
        z-index: 999;
        left: 0; top: 0;
        width: 100%; height: 100%;
        background-color: rgba(0,0,0,0.5);
    }
    .modal-content {
        background-color: #fff;
        margin: 10% auto;
        padding: 20px;
        border-radius: 8px;
        width: 400px;
        position: relative;
    }
    .modal-close {
        position: absolute;
        top: 10px; right: 15px;
        font-size: 24px;
        cursor: pointer;
    }
    .form-group {
        margin-bottom: 12px;
    }
    .form-group label {
        display: block;
        font-weight: bold;
    }
    .form-group input {
        width: 100%;
        padding: 6px;
    }
</style>
<!-- jQuery 포함 -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
>>>>>>> 7995e2b9579b40674fed2c410325aced6ed546d1
	
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
<<<<<<< HEAD
</div>
=======

    <!-- 회원가입 버튼 -->
    <button id="openSignupBtn">회원가입</button>
</div>
	
<!-- 회원가입 모달 -->
<div id="signupModal" class="modal">
    <div class="modal-content">
        <span class="modal-close" id="closeModalBtn">&times;</span>
        <h3>회원가입</h3>

        <form id="signupForm">
            <div class="form-group">
                <label for="signupMemId">아이디</label>
                <input type="text" id="signupMemId" name="memId" required>
            </div>
            <div class="form-group">
                <label for="signupMemPw">비밀번호</label>
                <input type="password" id="signupMemPw" name="memPw" required>
            </div>
            <div class="form-group">
                <label for="signupMemName">이름</label>
                <input type="text" id="signupMemName" name="memName" required>
            </div>
            <div class="form-group">
                <label for="signupPosNo">직책 번호</label>
                <input type="text" id="signupPosNo" name="posNo" required>
            </div>
            <div class="form-group">
                <label for="signupDepNo">부서 번호</label>
                <input type="text" id="signupDepNo" name="depNo" required>
            </div>

            <button type="submit">가입하기</button>
        </form>
    </div>
</div>

<script>
    // 모달 열기
    $('#openSignupBtn').on('click', function() {
        $('#signupModal').fadeIn();
    });

    // 모달 닫기
    $('#closeModalBtn').on('click', function() {
        $('#signupModal').fadeOut();
    });

    // 회원가입 폼 제출
    $('#signupForm').on('submit', function(e) {
        e.preventDefault();

        const signupData = {
            memId: $('#signupMemId').val(),
            memPw: $('#signupMemPw').val(),
            memName: $('#signupMemName').val(),
            posNo: $('#signupPosNo').val(),
            depNo: $('#signupDepNo').val()
        };

        $.ajax({
            url: '${pageContext.request.contextPath}/signup',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(signupData),
            success: function(response) {
                if (response === 'OK') {
                    alert('회원가입 성공!');
                    $('#signupModal').fadeOut();
                    $('#signupForm')[0].reset();
                } else {
                    alert('이미 사용 중인 아이디입니다.');
                }
            },
            error: function() {
                alert('회원가입 실패!');
            }
        });
    });
</script>
>>>>>>> 7995e2b9579b40674fed2c410325aced6ed546d1
