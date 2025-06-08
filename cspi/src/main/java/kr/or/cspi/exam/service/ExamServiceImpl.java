package kr.or.cspi.exam.service;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Service;

import kr.or.cspi.mapper.ExamMapper;
import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.ExamVO;

@Service
public class ExamServiceImpl implements ExamService {

	@Inject
	private ExamMapper examMapper;
	
	@Override
	public List<CspiExamVO> selectExamList() {
		return examMapper.selectExamList();
	}

}
