<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>


<h1>부서번호, 부서명을 차례로 입력해주세요.</h1>

<form id="deptInsert" action="/manager/testInsert" method="post">
	<input type="text" id="deptNoid" name="deptNo" /><br>
	<input type="text" id="deptNameid" name="deptName" /><br>
	<button id="saveButton">전송</button>
</form>

<script>
	document.getElementById('saveButton').addEventListener('click', function(event) {
		function validateAndSubmit() {
		    const deptNo = document.getElementById("deptNoid").value.trim();
		    const deptName = document.getElementById("deptNameid").value.trim();
		
		    if (deptNo === "" || deptName === "") {
		      alert("값을 입력해 주세요.");
		      return false; // 서버로 전송하지 않음
		    }
		
		    // 값이 있을 경우에만 submit
		    document.getElementById("deptInsert").submit();
		  }
	});
</script>
