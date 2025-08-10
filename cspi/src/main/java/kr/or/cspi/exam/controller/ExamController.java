package kr.or.cspi.exam.controller;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import kr.or.cspi.exam.service.ExamService;
import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.PaginationInfoVO;

@RequestMapping("/exam")
@Controller
public class ExamController {

	@Inject
	private ExamService examService;
	
	@RequestMapping("/cspiExamList.do")
	public String selectExamList(Model model, CspiExamVO examVO, String examNo,
			@RequestParam(name = "page", required = false, defaultValue = "1") int currentPage) {
		
		PaginationInfoVO<CspiExamVO> pagingVO = new PaginationInfoVO<CspiExamVO>();
		pagingVO.setExamNo(examNo);
		
		// 총 게시글 수
		int totalRecord = examService.selectExamListCount(pagingVO);
		pagingVO.setTotalRecord(totalRecord);
		
		// 현재 페이지 세팅
		pagingVO.setCurrentPage(currentPage);
		
		// 데이터 리스트
		List<CspiExamVO> cspiExamList = examService.selectExamList(pagingVO);
		pagingVO.setDataList(cspiExamList);
		
		model.addAttribute("pagingVO", pagingVO);
		model.addAttribute("examNo",examNo);
		
		return "test/exam/list";
	}
	
	@RequestMapping("/cspiExam.do")
	public String selectExam(Model model) {
		return "test/exam/exam";
	}
}
