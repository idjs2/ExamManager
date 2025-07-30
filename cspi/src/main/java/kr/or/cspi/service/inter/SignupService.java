package kr.or.cspi.service.inter;

import java.util.List;

import kr.or.cspi.vo.SignupVO;

public interface SignupService {

    boolean register(SignupVO signup);
    boolean isIdAvailable(String memId);

}
