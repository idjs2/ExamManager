package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.UserVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserMapper {

	UserVO authenticate(@Param("mem_id") String mem_id,
			@Param("mem_pw") String mem_pw);

}
