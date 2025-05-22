package kr.or.cspi.service;

import javax.servlet.http.HttpServletRequest;

import kr.or.cspi.ServiceResult;
import kr.or.cspi.vo.TestVO;

public interface TestService {
	public ServiceResult testInsert(HttpServletRequest req, TestVO testVO);
}
