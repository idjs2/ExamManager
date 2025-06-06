package kr.or.cspi.service.impl;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Service;

import kr.or.cspi.mapper.IMemberMapper;
import kr.or.cspi.service.inter.IMemberService;
import kr.or.cspi.vo.MemberVO;

@Service
public class MemberServiceImpl implements IMemberService {

	@Inject
	private IMemberMapper memberMapper;
	
	@Override
	public List<MemberVO> memberList() {
		// TODO Auto-generated method stub
		return memberMapper.memberList();
	}

}
