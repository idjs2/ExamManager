package kr.or.cspi.service.inter;

import java.util.List;

import kr.or.cspi.vo.UserVO;

public interface UserService {

	UserVO authenticate(String mem_id, String mem_pw);

}
