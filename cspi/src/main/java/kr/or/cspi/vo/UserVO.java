package kr.or.cspi.vo;

import lombok.Data;

@Data
public class UserVO {
	private String memId;
	private String memPw;
	
	public UserVO() {}
	public UserVO(String memId, String memPw) {
		this.memId = memId;
		this.memPw = memPw;
	}

}
