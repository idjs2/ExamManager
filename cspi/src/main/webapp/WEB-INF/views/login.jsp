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
    .form-justify {
    	display:flex;
    	justify-content:space-between;
    	align-items:center;
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
    <!-- 비밀번호 초기화 버튼 -->
    <button id="openPwdResetBtn">비밀번호 초기화</button>
</div>
	
<!-- 회원가입 모달 -->
<div id="signupModal" class="modal">
    <div class="modal-content">
        <span class="modal-close" id="closeSignupBtn">&times;</span>
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
<!--             <div class="form-group">
                <label for="signupPosNo">직책 번호</label>
                <input type="text" id="signupPosNo" name="posNo" required>
            </div>
            <div class="form-group">
                <label for="signupDepNo">부서 번호</label>
                <input type="text" id="signupDepNo" name="depNo" required>
            </div> -->
            <div>
            	<label for="signupPos" class="form-label">직급</label>
            	<select id="signupPos" name="posNo" class="form-select">
            		<option value="">..</option>
            	</select>
            </div>
            <div>
            	<label for="signupDep" class="form-label">부서</label>
            	<select id="signupDep" name="depNo" class="form-select">
            		<option value="">..</option>
            	</select>
            </div>
            
			<div class="form-justify">
				<label><input type="checkbox" id="adminAuth" disabled>관리자 권한</label>
	            <button type="submit">가입하기</button>
			</div>

        </form>
    </div>
</div>

<!-- 비밀번호 초기화 모달 -->
<div id="pwdresetModal" class="modal">
    <div class="modal-content">
        <span class="modal-close" id="closePwdResetBtn">&times;</span>
        <h3>비밀번호 초기화</h3>

        <form id="pwdresetForm">
            <div class="form-group">
                <label for="pwdresetMemId">아이디</label>
                <input type="text" id="pwdresetMemId" name="memId" required>
            </div>
            <div class="form-group">
                <label for="pwdresetMemName">이름</label>
                <input type="text" id="pwdresetMemName" name="memName" required>
            </div>
<!--             <div class="form-group">
                <label for="pwdresetPosNo">직책 번호</label>
                <input type="text" id="pwdresetPosNo" name="posNo" required>
            </div>
            <div class="form-group">
                <label for="pwdresetDepNo">부서 번호</label>
                <input type="text" id="pwdresetDepNo" name="depNo" required>
            </div> -->

            <button type="submit">초기화</button>
        </form>
    </div>
</div>


<script>
	// 회원가입 모달
    $('#openSignupBtn').on('click', function() {  // 모달 열기
        $('#signupModal').fadeIn();
    });
    $('#closeSignupBtn').on('click', function() {  // 모달 닫기
        $('#signupModal').fadeOut();
    });

    $('#signupForm').on('submit', function(e) {  // 회원가입 폼 제출
        e.preventDefault();

        const signupData = {
            memId: $('#signupMemId').val(),
            memPw: $('#signupMemPw').val(),
            memName: $('#signupMemName').val(),
            posNo: $('#signupPos').val(),
            depNo: $('#signupDep').val()
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
    
    
    
 	// 비밀번호 초기화 모달
    $('#openPwdResetBtn').on('click', function() {  // 모달 열기
        $('#pwdresetModal').fadeIn();
    });

    $('#closePwdResetBtn').on('click', function() {  // 모달 닫기
        $('#pwdresetModal').fadeOut();
    });
    
    $('#pwdresetForm').on('submit', function(e) {  // 초기화 정보 제출
        e.preventDefault();
    
        const pwdresetData = {
                memId: $('#pwdresetMemId').val(),
                memName: $('#pwdresetMemName').val(),
                posNo: $('#pwdresetPos').val(),
                depNo: $('#pwdresetDep').val()
            };

            $.ajax({
                url: '${pageContext.request.contextPath}/pwdreset',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(pwdresetData),
                success: function(response) {
                    if (response === 'OK') {
                        alert('회원가입 성공!');
                        $('#pwdresetModal').fadeOut();
                        $('#pwdresetForm')[0].reset();
                    } else {
                        alert('이미 사용 중인 아이디입니다.');
                    }
                },
                error: function() {
                    alert('회원가입 실패!');
                }
            });
        });
    
    // 드롭다운 박스 (직급,부서)

   	// 직급 데이터 AJAX 호출
   	$.getJSON('/signup/positions', function(data) {
   		const positionSelect = $('#signupPos');
   		positionSelect.empty().append('<option value="">선택</option>');
   		$.each(data, function(i,pos) {
   			positionSelect.append('<option value="' + pos.posNo + '">' + pos.posName + '</option>');
   		});
   	});
   	// 부서 데이터 AJAX 호출
   	$.getJSON('/signup/departments', function(data) {
   		const departmentSelect = $('#signupDep');
   		departmentSelect.empty().append('<option value="">선택</option>');
   		$.each(data, function(i,dep) {
   			departmentSelect.append('<option value="' + dep.depNo + '">' + dep.depName + '</option>');
   		});
   	});

    
    // 관리자 권한
   	const selectPosition = document.getElementById("signupPos");
    const adminCheck = document.getElementById("adminAuth");
    
   	selectPosition.addEventListener("change", function() {
   		const authRanks = ["차장", "부장", "이사", "상무"];
   		const selectText = this.options[this.selectedIndex].text;
   		
   		if (authRanks.includes(selectText)) {
   			adminCheck.disabled = false;
   		} else {
   			adminCheck.checked = false;
   			adminCheck.disabled = true;
   		}
   	});
    
</script>