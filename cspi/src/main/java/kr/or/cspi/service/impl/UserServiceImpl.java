package kr.or.cspi.service.impl;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Service;

import kr.or.cspi.mapper.UserMapper;
import kr.or.cspi.service.inter.UserService;
import kr.or.cspi.vo.UserVO;

@Service
public class UserServiceImpl implements UserService {

    @Inject
    private UserMapper userMapper;

    @Override
    public UserVO authenticate(String mem_id, String mem_pw) {
        return userMapper.authenticate(mem_id, mem_pw);
    }
}
