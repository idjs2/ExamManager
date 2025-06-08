package kr.or.cspi.controller.login;

import java.util.List;

import javax.inject.Inject;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import kr.or.cspi.service.inter.UserService;
import kr.or.cspi.vo.UserVO;

@RequestMapping("/login")
@Controller
public class LoginController {
	
	@Inject
	private UserService userService;

    // 로그인 폼
    @GetMapping("/loginForm.do")
    public String loginForm() {
        return "login";  // /WEB-INF/views/login.jsp
    }

    // 로그인 처리
    @PostMapping("/loginProc.do")
    public String login(@RequestParam String memId,
                        @RequestParam String memPw,
                        HttpSession session,
                        HttpServletResponse response,
                        Model model) {
//        System.out.println("입력된 ID: " + memId);
//        System.out.println("입력된 PW: " + memPw);

        UserVO user = userService.authenticate(memId, memPw);  // 얘가 계속 null값을 보낸다?
//        System.out.println("쿼리 결과 User: " + user); // null이면 쿼리 결과 없음
        
        if (user != null) {
            session.setAttribute("user", user);
            
            // 쿠키에 최근 로그인 ID 저장 (유효기간: 7일)
            Cookie idCookie = new Cookie("lastLoginId", memId);
            idCookie.setPath("/"); // 모든 경로에서 유효
            idCookie.setMaxAge(7 * 24 * 60 * 60); // 7일
            response.addCookie(idCookie);
            
            return "redirect:/home.do";  // home 페이지 URL 예시
        } else {
            model.addAttribute("error", "아이디 또는 비밀번호가 일치하지 않습니다.");
            return "login";  // 로그인 실패 시 다시 로그인 페이지
        }
    }

    // 로그아웃
    @GetMapping("/logout.do")
    public String logout(HttpSession session) {
    	UserVO user = (UserVO) session.getAttribute("user");
    	
        if (user != null) {
            session.setAttribute("lastLoginId", user.getMemId());
        }
    	
        session.invalidate();
        return "redirect:/login/loginForm.do";
    }
}
