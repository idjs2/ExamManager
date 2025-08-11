package kr.or.cspi.service.impl;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

import kr.or.cspi.mapper.SignupMapper;
import kr.or.cspi.service.inter.SignupService;
import kr.or.cspi.vo.SignupVO;
import kr.or.cspi.vo.PositionVO;
import kr.or.cspi.vo.DepartmentVO;

@Service
public class SignupServiceImpl implements SignupService {

    @Autowired
    private SignupMapper signupMapper;

    @Override
    public boolean register(SignupVO signup) {
        // 중복 아이디 체크
        if (signupMapper.countById(signup.getMemId()) > 0) {
            return false;
        }
        return signupMapper.insertMember(signup) > 0;
    }

    @Override
    public boolean isIdAvailable(String memId) {
        return signupMapper.countById(memId) == 0;
    }

    @Override
    public List<PositionVO> getPositions() {
    	return  signupMapper.getPositions();
    }

    @Override
    public List<DepartmentVO> getDepartments() {
    	return  signupMapper.getDepartments();
    }
}
