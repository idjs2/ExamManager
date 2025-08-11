package kr.or.cspi.vo;

import lombok.Data;

@Data
public class SignupVO {
    private String memId;
    private String memPw;
    private String memName;
    private String depNo;
    private String posNo;
    private boolean adminAuth;
    
    public SignupVO() {}  // lombok 만으로는 생성자가 생성되지 않는다?
	public SignupVO(String memId, String memPw, String memName, String posNo, String depNo, boolean adminAuth) {
		this.memId = memId;
		this.memPw = memPw;
		this.memName = memName;
		this.posNo = posNo;
		this.depNo = depNo;
		this.adminAuth = adminAuth;
	}
}
