package kr.or.cspi.vo;

import lombok.Data;

@Data
public class CspiExamVO {
	private String ceId;
	private String examNo;
	private String ceName;
	private String ceExp;
	private String ceYear;
	private Integer ceRound;
	private String ceDate;
	private String fileGroupNo;
	
	private int rnum; //페이징 처리를 위해 추가

}
