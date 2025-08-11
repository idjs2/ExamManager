package kr.or.cspi.controller.login;

import java.util.List;

import javax.inject.Inject;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;

import kr.or.cspi.service.inter.PwdChangeService;
import kr.or.cspi.vo.PwdChangeVO;

@RequestMapping("/pwdchange")
@RestController
public class PwdChangeController {
	
    @Autowired
    private PwdChangeService pwdchangeService;

    @PostMapping  // 가입 버튼 누르면 진행
    public String change(@RequestBody PwdChangeVO pwdchange) {
        return pwdchangeService.ChangePw(pwdchange) ? "OK" : "DUPLICATE_ID";
    }
    
    @GetMapping("/checkPw")  // 가입 버튼을 누르기 전에 지속효과 - 사용자가 회원가입 폼에 아이디를 입력할 때 비동기 AJAX 요청으로 호출
    public boolean checkPw(@RequestParam String memId) {
        return pwdchangeService.CheckingId(memId);
    }
    
    
}
