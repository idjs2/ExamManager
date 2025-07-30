package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.SignupVO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SignupMapper {

    // 아이디 중복 체크
    int countById(String memId);

    // 회원 정보 등록
    int insertMember(SignupVO signup);

}
