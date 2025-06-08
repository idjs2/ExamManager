package kr.or.cspi.controller.member;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import kr.or.cspi.service.inter.IMemberService;
import kr.or.cspi.vo.MemberVO;

@RequestMapping("/member")
@Controller
public class MemberController {

	@Inject
	private IMemberService memberService;

	//슈퍼베이스 연동 확인용
	@GetMapping("/memberList.do")
	public String selectMemberList(Model model, MemberVO memberVO) {

		List<MemberVO> memberList = memberService.memberList();
		model.addAttribute("memberList", memberList);

		return "test/main";
	}
}
