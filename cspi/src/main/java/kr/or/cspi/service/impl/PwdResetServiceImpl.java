package kr.or.cspi.service.impl;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

import kr.or.cspi.mapper.PwdResetMapper;
import kr.or.cspi.service.inter.PwdResetService;
import kr.or.cspi.vo.PwdResetVO;

@Service
public class PwdResetServiceImpl implements PwdResetService {

    @Autowired
    private PwdResetMapper pwdresetMapper;

    @Override
    public boolean ChangePw(PwdResetVO pwdreset) {
        // 중복 아이디 체크
        if (pwdresetMapper.checkId(pwdreset.getMemId()) > 0) {
            return false;
        }
        return pwdresetMapper.PwdChange(pwdreset) > 0;
    }

    @Override
    public boolean CheckingId(String memId) {
        return pwdresetMapper.checkId(memId) == 0;
    }
}
