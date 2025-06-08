package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.UserVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserMapper {

	UserVO authenticate(@Param("memId") String memId,
			@Param("memPw") String memPw);

}
