package kr.or.cspi.service.inter;

import java.util.List;

import kr.or.cspi.vo.PwdResetVO;

public interface PwdResetService {

    boolean ChangePw(PwdResetVO pwdreset);
    boolean CheckingId(String memId);

}
