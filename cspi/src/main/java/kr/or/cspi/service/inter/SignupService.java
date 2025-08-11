package kr.or.cspi.service.inter;

import java.util.List;

import kr.or.cspi.vo.SignupVO;
import kr.or.cspi.vo.PositionVO;
import kr.or.cspi.vo.DepartmentVO;

public interface SignupService {

    boolean register(SignupVO signup);
    boolean isIdAvailable(String memId);
    
    List<PositionVO> getPositions();
    List<DepartmentVO> getDepartments();

}
