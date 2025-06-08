package kr.or.cspi.exam.controller;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

import kr.or.cspi.exam.service.ExamService;
import kr.or.cspi.vo.ExamVO;

@RequestMapping("/exam")
@Controller
public class ExamController {

	@Inject
	private ExamService examService;
	
	@RequestMapping("/examList.do")
	public String selectExamList(Model model, ExamVO examVO) {
		List<ExamVO> examList = examService.selectExamList();
		model.addAttribute("examList",examList);
		return "test/exam/list";
	}
}
