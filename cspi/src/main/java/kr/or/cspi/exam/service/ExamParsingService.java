package kr.or.cspi.exam.service;

import java.util.List;

import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.ExamVO;
import kr.or.cspi.vo.PaginationInfoVO;

public interface ExamParsingService {

    void processExamPdf(String pdfPath, String ceName) throws Exception;

}
