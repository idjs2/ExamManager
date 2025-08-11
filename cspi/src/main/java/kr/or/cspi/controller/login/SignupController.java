package kr.or.cspi.controller.login;

import java.util.List;

import javax.inject.Inject;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;

import kr.or.cspi.service.inter.SignupService;
import kr.or.cspi.vo.SignupVO;
import kr.or.cspi.vo.PositionVO;
import kr.or.cspi.vo.DepartmentVO;

@RequestMapping("/signup")
@RestController
public class SignupController {
	
    @Autowired
    private SignupService signupService;

    @PostMapping  // 가입 버튼 누르면 진행
    public String register(@RequestBody SignupVO signup) {
        return signupService.register(signup) ? "OK" : "DUPLICATE_ID";
    }
    
    @GetMapping("/checkId")  // 가입 버튼을 누르기 전에 지속효과 - 사용자가 회원가입 폼에 아이디를 입력할 때 비동기 AJAX 요청으로 호출
    public boolean checkId(@RequestParam String memId) {
        return signupService.isIdAvailable(memId);
    }
    
    @GetMapping("/positions")
    public List<PositionVO> getPositions() {
    	return signupService.getPositions();
    }

    @GetMapping("/departments")
    public List<DepartmentVO> getDepartments() {
    	return signupService.getDepartments();
    }
    
}
