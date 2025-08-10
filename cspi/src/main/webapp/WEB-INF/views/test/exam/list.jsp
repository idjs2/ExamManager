<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>    
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt" prefix="fmt" %>

<div class="container-fluid">
    <h1 class="h3 mb-2 text-gray-800">시험목록</h1>

    <div class="card shadow mb-4">
        <div class="card-header py-3 d-flex justify-content-between align-items-center">
            <h6 class="m-0 font-weight-bold text-primary">자격시험</h6>
            <button type="button" class="btn btn-primary" id="insertBtn">시험등록</button>
        </div>

        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-bordered dataTable" id="dataTable" width="100%" cellspacing="0">
                    <thead>
                        <tr>
                            <th>번호</th>
                            <th>시험명</th>
                            <th>설명</th>
                            <th>년도</th>
                            <th>회차</th>
                            <th>등록일</th>
                        </tr>
                    </thead>
                    <tbody>
                        <c:choose>
                            <c:when test="${empty pagingVO.dataList}">
                                <tr>
                                    <td colspan="6" class="text-center">조회하신 게시글이 존재하지 않습니다.</td>
                                </tr>
                            </c:when>
                            <c:otherwise>
                                <c:forEach items="${pagingVO.dataList}" var="cspiExam">
                                    <tr>
                                        <td>${cspiExam.rnum}</td>
                                        <td><a href="/exam/detail.do?ceId=${cspiExam.ceId}">${cspiExam.ceName}</a></td>
                                        <td><a href="/exam/detail.do?ceId=${cspiExam.ceId}">${cspiExam.ceExp}</a></td>
                                       <%--  <fmt:parseDate var="regdate" pattern="yyyy-MM-dd HH:mm:ss.SSS" value="${cspiExam.ceDate}" /> --%>
                                        <%-- <fmt:formatDate var="regdate" pattern="yyyy-MM-dd" value="${regdate}" /> --%>
                                        <td>${cspiExam.ceYear}</td>
                                        <td>${cspiExam.ceRound}</td>
                                        <td>${cspiExam.ceDate}</td>
                                    </tr>
                                </c:forEach>
                            </c:otherwise>
                        </c:choose>
                    </tbody>
                </table>
            </div>

            <!-- 페이징 영역 -->
            <div class="card-footer clearfix" id="pagingArea">
                ${pagingVO.pagingHTML}
            </div>

            <!-- 페이지 이동용 폼 -->
            <form id="pageInfo" method="get">
                <input type="hidden" name="page" id="page">
                <input type="hidden" name="examNo" value="${examNo}">
            </form>
        </div>
    </div>
</div>

<!-- 스크립트 -->
<script type="text/javascript">
document.addEventListener("DOMContentLoaded", function() {
    var pagingArea = document.getElementById("pagingArea");
    var pageInfo = document.getElementById("pageInfo");
    var pageInput = document.getElementById("page");

    // 페이징 클릭 이벤트 (이벤트 위임)
    pagingArea.addEventListener("click", function(event) {
        var target = event.target;

        // a 태그인지, 그리고 data-page 속성이 있는지 확인
        if (target.tagName === "A" && target.hasAttribute("data-page")) {
            event.preventDefault();
            var pageNo = target.getAttribute("data-page");
            pageInput.value = pageNo;
            pageInfo.submit();
        }
    });

    // 시험등록 버튼 클릭 이벤트
    var insertBtn = document.getElementById("insertBtn");
    insertBtn.addEventListener("click", function() {
        location.href = "/exam/examDataForm.do?examNo=${param.examNo}";
    });
});

</script>
