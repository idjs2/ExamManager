package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.PwdChangeVO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PwdChangeMapper {

    // 아이디 확인
    int checkId(String memId);

    // 비밀번호 변경
    int PwdChange(PwdChangeVO pwdchange);

}
