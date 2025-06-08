package kr.or.cspi.exam.service;

import java.util.List;

import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.ExamVO;

public interface ExamService {

	List<CspiExamVO> selectExamList();

}
