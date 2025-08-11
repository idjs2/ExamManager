package kr.or.cspi.service.impl;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

import kr.or.cspi.mapper.PwdChangeMapper;
import kr.or.cspi.service.inter.PwdChangeService;
import kr.or.cspi.vo.PwdChangeVO;

@Service
public class PwdChangeServiceImpl implements PwdChangeService {

    @Autowired
    private PwdChangeMapper pwdchangeMapper;

    @Override
    public boolean ChangePw(PwdChangeVO pwdchange) {
        // 중복 아이디 체크
        if (pwdchangeMapper.checkId(pwdchange.getMemId()) > 0) {
            return false;
        }
        return pwdchangeMapper.PwdChange(pwdchange) > 0;
    }

    @Override
    public boolean CheckingId(String memId) {
        return pwdchangeMapper.checkId(memId) == 0;
    }
}
