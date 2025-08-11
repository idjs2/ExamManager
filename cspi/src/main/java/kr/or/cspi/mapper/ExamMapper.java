package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.ExamVO;
import kr.or.cspi.vo.PaginationInfoVO;

public interface ExamMapper {

	int selectExamListCount(PaginationInfoVO<CspiExamVO> pagingVO);

	List<CspiExamVO> selectExamList(PaginationInfoVO<CspiExamVO> pagingVO);

}
