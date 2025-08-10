package kr.or.cspi.vo;

import lombok.Data;

@Data
public class PwdResetVO {
    private String memId;
    private String memPw;
    private String memName;
    private String depNo;
    private String posNo;
    
    public PwdResetVO() {}
	public PwdResetVO(String memId, String memPw, String memName, String posNo, String depNo) {
		this.memId = memId;
		this.memPw = memPw;
		this.memName = memName;
		this.posNo = posNo;
		this.depNo = depNo;
	}
}
