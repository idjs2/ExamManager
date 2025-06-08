package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.ExamVO;

public interface ExamMapper {

	List<CspiExamVO> selectExamList();

}
