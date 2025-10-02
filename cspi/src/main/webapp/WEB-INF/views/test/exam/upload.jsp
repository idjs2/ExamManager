<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>	
	
<html>
<head>
    <title>시험 업로드</title>
</head>
<body>
    <h2>시험 업로드</h2>
    <form action="${pageContext.request.contextPath}/exam/upload" method="post" enctype="multipart/form-data">
        <label>시험 이름:</label>
        <input type="text" name="ceName" required><br><br>
        <p>연도/시험명/회차  ex) 2020 정보처리기사 1회차</p>

        <label>시험 PDF 업로드:</label>
        <input type="file" name="file" accept="application/pdf" required><br><br>

        <button type="submit">업로드</button>
    </form>
</body>
</html>