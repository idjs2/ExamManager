package kr.or.cspi.vo;

import lombok.Data;

@Data
public class UserVO {
	private String mem_id;
	private String mem_pw;
	
	public UserVO() {}
	public UserVO(String mem_id, String mem_pw) {
		this.mem_id = mem_id;
		this.mem_pw = mem_pw;
	}
	
//	public String getMemberID() {return mem_id;}
//	public void setMemberID(String mem_id) {this.mem_id = mem_id;}
//	
//	public String getMemberPW() {return mem_pw;}
//	public void setMemberPW(String mem_pw) {this.mem_pw = mem_pw;}
}
