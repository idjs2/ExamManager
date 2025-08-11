package kr.or.cspi.exam.service;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Service;

import kr.or.cspi.mapper.ExamMapper;
import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.ExamVO;
import kr.or.cspi.vo.PaginationInfoVO;

@Service
public class ExamServiceImpl implements ExamService {

	@Inject
	private ExamMapper examMapper;
	
	@Override
	public int selectExamListCount(PaginationInfoVO<CspiExamVO> pagingVO) {
		// TODO Auto-generated method stub
		return examMapper.selectExamListCount(pagingVO);
	}
	
	@Override
	public List<CspiExamVO> selectExamList(PaginationInfoVO<CspiExamVO> pagingVO) {
		return examMapper.selectExamList(pagingVO);
	}


}
