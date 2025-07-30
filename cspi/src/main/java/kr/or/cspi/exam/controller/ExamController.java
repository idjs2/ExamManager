package kr.or.cspi.exam.controller;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

import kr.or.cspi.exam.service.ExamService;
import kr.or.cspi.vo.CspiExamVO;

@RequestMapping("/exam")
@Controller
public class ExamController {

	@Inject
	private ExamService examService;
	
	@RequestMapping("/cspiExamList.do")
	public String selectExamList(Model model, CspiExamVO examVO) {
		List<CspiExamVO> cspiExamList = examService.selectExamList();
		model.addAttribute("cspiExamList",cspiExamList);
		return "test/exam/list";
	}
	
	@RequestMapping("/cspiExam.do")
	public String selectExam(Model model) {
		return "test/exam/exam";
	}
}
