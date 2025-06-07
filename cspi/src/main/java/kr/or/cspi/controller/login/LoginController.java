package kr.or.cspi.controller.login;

import java.util.List;

import javax.inject.Inject;
import javax.servlet.http.HttpSession;

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

    // �α��� ��
    @GetMapping("/loginForm.do")
    public String loginForm() {
        return "test/login";  // /WEB-INF/views/test/login.jsp
    }

    // �α��� ó��
    @PostMapping("/loginProc.do")
    public String login(@RequestParam String mem_id,
                        @RequestParam String mem_pw,
                        HttpSession session,
                        Model model) {
        System.out.println("�Էµ� ID: " + mem_id);
        System.out.println("�Էµ� PW: " + mem_pw);

        UserVO user = userService.authenticate(mem_id, mem_pw);  // �갡 ��� null���� ������?

        if (user != null) {
            session.setAttribute("user", user);
            return "redirect:/home/home.do";  // home ������ URL ����
        } else {
            model.addAttribute("error", "���̵� �Ǵ� ��й�ȣ�� ��ġ���� �ʽ��ϴ�.");
            return "test/login";  // �α��� ���� �� �ٽ� �α��� ������
        }
    }

    // �α׾ƿ�
    @GetMapping("/logout.do")
    public String logout(HttpSession session) {
        session.invalidate();
        return "test/login";
    }
}
