package kr.or.cspi.exam.controller;

import java.util.List;

import javax.inject.Inject;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;

import kr.or.cspi.exam.service.ExamParsingService;

import java.io.File;

@Controller
@RequestMapping("/exam")
public class ExamUploadController {

    private final ExamParsingService examParsingService;

    public ExamUploadController(ExamParsingService examParsingService) {
        this.examParsingService = examParsingService;
    }
    
    @GetMapping(value = "/upload", produces = "text/plain;charset=UTF-8")
    public String uploadForm() {
        return "test/exam/upload";
    }

    @PostMapping(value = "/upload", produces = "text/plain;charset=UTF-8")
    public ResponseEntity<String> uploadExam(@RequestParam("file") MultipartFile file,
                                             @RequestParam("ceName") String ceName) {
        try {
            // 1. raw_data 폴더에 저장
            String uploadDir = "C:/CSPI/ExamManager/cspi/src/main/resources/python/data/raw_data/information_processing/";
            File dest = new File(uploadDir, file.getOriginalFilename());
            file.transferTo(dest); // 원본 저장

            // 2. Service 호출 → Python 실행 + JSON 파싱 → DB 저장
            examParsingService.processExamPdf(dest.getAbsolutePath(), ceName);

            return ResponseEntity.ok("시험 등록 및 DB 저장 완료!");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                                 .body("오류 발생: " + e.getMessage());
        }
    }
}
