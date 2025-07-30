<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
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
	
<div class="container-fluid">
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