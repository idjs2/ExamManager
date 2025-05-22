package kr.or.cspi.mapper;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;

import kr.or.cspi.vo.TestVO;

@Mapper
public interface TestMapper {
	public int testInsert(TestVO testVO);
}
