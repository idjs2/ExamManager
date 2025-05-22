package kr.or.cspi.controller;

import java.util.HashMap;
import java.util.Map;

import javax.inject.Inject;
import javax.servlet.http.HttpServletRequest;

import org.apache.commons.lang.StringUtils;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import kr.or.cspi.ServiceResult;
import kr.or.cspi.service.TestService;
import kr.or.cspi.vo.TestVO;

@Controller
@RequestMapping("/manager")
public class TestController {

	@Inject
	private TestService testService;	

	
	@GetMapping("/testInsert")
	public String insertView() {
		return "test/test1";
	}
	@GetMapping("/testInsertSuccess")
	public String SuccessView() {
		return "test/testSuccess";
	}
	
	@PostMapping("/testInsert")
	public String testInsert(String deptNo, String deptName, TestVO testVO, Model model, HttpServletRequest req) {
		String goPage = "";
		Map<String, String> errors = new HashMap<String, String>();
		if (StringUtils.isBlank(testVO.getDeptNo())) {
		    errors.put("deptNo", "부서번호를 입력해주세요!");
		}
		if (StringUtils.isBlank(testVO.getDeptName())) {
		    errors.put("deptName", "부서명을 입력해주세요!");
		}
		
		if (errors.size() > 0) {
			model.addAttribute("errors" , errors);
			model.addAttribute("TestVO", testVO);
			goPage = "test/test1";
		}else { // 등록 성공
			testVO.setDeptNo(deptNo);
			ServiceResult result = testService.testInsert(req, testVO);
			if (result.equals(ServiceResult.OK)) {// 등록 성공 assNo=ASS_20240042&lecNo=L0103
				goPage = "test/testSuccess";
			}
		}
		return goPage;
	}
}
