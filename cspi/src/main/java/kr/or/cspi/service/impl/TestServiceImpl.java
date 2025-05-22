package kr.or.cspi.service.impl;


import javax.inject.Inject;
import javax.servlet.http.HttpServletRequest;

import org.springframework.stereotype.Service;

import kr.or.cspi.ServiceResult;
import kr.or.cspi.vo.TestVO;
import kr.or.cspi.mapper.TestMapper;
import kr.or.cspi.service.TestService;

@Service
public class TestServiceImpl implements TestService {
	
	@Inject
	private TestMapper testMapper;
	
	@Override
	public ServiceResult testInsert(HttpServletRequest req, TestVO testVO) {
		ServiceResult result = null;

		int status = testMapper.testInsert(testVO);
		if (status > 0) {
			result = ServiceResult.OK;
		} else {
			result = ServiceResult.FAILED;
		}

		return result;
	}
}
