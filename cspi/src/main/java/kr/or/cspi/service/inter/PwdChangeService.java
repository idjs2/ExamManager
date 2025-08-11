package kr.or.cspi.service.inter;

import java.util.List;

import kr.or.cspi.vo.PwdChangeVO;

public interface PwdChangeService {

    boolean ChangePw(PwdChangeVO pwdchange);
    boolean CheckingId(String memId);

}
