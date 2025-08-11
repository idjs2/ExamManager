package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.SignupVO;
import kr.or.cspi.vo.PositionVO;
import kr.or.cspi.vo.DepartmentVO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SignupMapper {

    // 아이디 중복 체크
    int countById(String memId);

    // 회원 정보 등록
    int insertMember(SignupVO signup);
    
    // 직급, 부서 드롭다운
    List<PositionVO> getPositions();
    List<DepartmentVO> getDepartments();

}
