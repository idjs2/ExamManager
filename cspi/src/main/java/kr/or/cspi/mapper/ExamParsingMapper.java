package kr.or.cspi.mapper;

import java.util.List;

import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.QuestionVO;
import kr.or.cspi.vo.OptionVO;
import kr.or.cspi.vo.PaginationInfoVO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface ExamParsingMapper {

    void insertExam(CspiExamVO examVO);
    void insertQuestion(QuestionVO questionVO);
    void insertOption(OptionVO optionVO);

    String getLastCeId();
    Integer selectMaxExamId();
    Integer getLastCeRound();
}
