package kr.or.cspi.exam.service;

import java.util.List;
import java.util.ArrayList;
import javax.inject.Inject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.LocalDate;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;  // JAVA에서 json<->객체 변환할 때 많이 씀
import kr.or.cspi.mapper.ExamParsingMapper;
import kr.or.cspi.vo.CspiExamVO;
import kr.or.cspi.vo.QuestionVO;
import kr.or.cspi.vo.OptionVO;

import java.nio.charset.StandardCharsets;
import org.apache.commons.io.FilenameUtils;
import org.springframework.stereotype.Service;
import org.springframework.core.io.ClassPathResource;  // ClassPath
import org.springframework.transaction.annotation.Transactional;

import org.springframework.beans.factory.annotation.Value;
import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

import java.security.MessageDigest;

@Service
public class ExamParsingServiceImpl implements ExamParsingService {

    @Inject
    private ExamParsingMapper examParsingMapper;

    @Value("${python.exec}")
    private String pythonExec;  // python.exec=C:/Users/idjs1/AppData/Local/Programs/Python/Python311/python.exe
    
    @Value("${python.script.dir}")  // python.script.dir=python
    private String pythonScriptDir;

    @Value("${python.script.name}")  // python.script.name=exam_parser.py
    private String pythonScriptName;
    
    @Value("${python.output.dir}")  // python.output.dir=C:/CSPI/ExamManager/cspi/output
    private String outputDir;
    
    
    private String safeBaseName(String baseName) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] digest = md.digest(baseName.getBytes(StandardCharsets.UTF_8));
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 4; i++) { // 8자리만
            sb.append(String.format("%02x", digest[i]));
        }
        return sb.toString();
    }
    
    /**
     * PDF 파일을 파싱하여 DB에 시험/문제/선택지 저장
     * 모든 과정은 트랜잭션으로 묶임
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void processExamPdf(String pdfPath, String ceName) throws Exception {
        // -------------------------------
        // 1. Python 스크립트 실행
        // -------------------------------
    	
        // Python 스크립트 실행 경로 지정
    	// File scriptDir = new File(pythonScriptDir);
    	File scriptDir = new ClassPathResource(pythonScriptDir).getFile();
        
        ProcessBuilder pb = new ProcessBuilder(  // 자바에서 ProcessBuilder가 실행하는 건 윈도우 CMD 환경 기준
        		pythonExec,
        		pythonScriptName, 
        		pdfPath);  // 명령어 형태로 출력 준비 -> python exam_parser.py C:/CSPI/ExamManager/raw_data/정보처리기사20210814.pdf
        pb.environment().put("PYTHONIOENCODING", "utf-8");  // 콘솔과 스트림 인코딩 강제
        pb.directory(scriptDir);  // 명령어 실행 위치 지정 src/main/resources/python
        pb.redirectErrorStream(true);  // 에러 메시지도 출력 스트림에서 함께 읽음

        Process process = pb.start();  // 명령어 실행
        
        // Python 실행 로그 확인 : 파이썬 스크립트 실행 결과를 자바에서 실시간으로 읽어와서 콘솔에 출력해 주는 로직
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("[PYTHON] " + line);
            }
        }

        // -------------------------------
        // 2. JSON 결과 파일 경로 구성
        // -------------------------------

        int exitCode = process.waitFor();  // Python 프로세스 끝날 때까지 대기
        if (exitCode != 0) {  // 0 : 정상 종료
            throw new RuntimeException("Python script 실행 실패 (exitCode=" + exitCode + ")");
        }


     // JSON 파일 경로 만들기
        String baseName = FilenameUtils.getBaseName(pdfPath); // 원본 파일명  ex) "정보처리기사20210814(학생용)"
        String safeName = safeBaseName(baseName);
        Path jsonFilePath = Paths.get(
        		outputDir,
                "output_" + safeName,
                "information_processing_parsed_questions.json"
        );

        // 해당 파일이 존재하는지 확인
        File jsonFile = jsonFilePath.toFile();
        if (!jsonFile.exists()) {
            throw new RuntimeException("❌ JSON 파일이 존재하지 않습니다: " + jsonFile.getAbsolutePath());
        }

        // -------------------------------
        // 3. JSON 파싱
        // -------------------------------
        ObjectMapper mapper = new ObjectMapper();
        List<Map<String, Object>> questions = mapper.readValue(
                jsonFile, new TypeReference<List<Map<String, Object>>>() {}  // JAVA에 맞게 구조를 잡아서 가져옴
        );  // Map = Python 딕셔너리랑 같은 듯

        // -------------------------------
        // 4. cspi_exam 테이블 insert
        // -------------------------------
        CspiExamVO cspiexamVO = new CspiExamVO();
        String ceId = generateCeId();  // 새로운 시험 ID 생성 (예: CE001 → CE002)
        Integer ceRound = generateCeRound();
        
        cspiexamVO.setCeId(ceId);  // 삽입될 때마다 1씩 추가되야함. 아직  없음
        cspiexamVO.setExamNo("E002");   // 정보처리기사
        cspiexamVO.setCeName(ceName);  // 직접 입력해서 넘겨받음
        cspiexamVO.setCeExp(null);   // 일단 null
        cspiexamVO.setCeYear(extractYearFromFilename(baseName));
        cspiexamVO.setCeRound(ceRound); // 일단 null
        cspiexamVO.setCeDate(LocalDate.now().toString());  // 오늘 날짜
        cspiexamVO.setFileGroupNo(null);
        examParsingMapper.insertExam(cspiexamVO);

        // -------------------------------
        // 5. question + options insert
        // -------------------------------
        for (Map<String, Object> q : questions) {
            // Question VO
            QuestionVO questionVO = new QuestionVO();
            String queNo = generateQueNo((Integer) q.get("question_number"));
            questionVO.setQueNo(queNo);
            questionVO.setCeId(ceId);
            questionVO.setQueSub((String) q.get("question_text"));
            questionVO.setQueExp((String) q.get("subject"));
            questionVO.setQueFile((String) q.get("image_path"));
            questionVO.setQueScore(5);
            questionVO.setQueAnswer(q.get("answer").toString()); // 숫자/문자 상관없이 String 처리
            questionVO.setFileGroupNo(null);
            questionVO.setOptionType((String) q.get("option_type"));
            examParsingMapper.insertQuestion(questionVO);

            // Options VO
            // List<String> options = (List<String>) q.get("options");  // json을 JACKSON으로 읽으면서 생긴 타입 문제로 아래 걸로 수정함
            Object optionsObj = q.get("options");
            List<String> options = new ArrayList<>();
            if (optionsObj instanceof List<?>) {
                for (Object o : (List<?>) optionsObj) {
                    options.add(o.toString());
                }
            }
            
            int optIdx = 1;
            for (String optContent : options) {
                OptionVO optionVO = new OptionVO();
                optionVO.setOptionNo(generateOptNo(optIdx));
                optionVO.setQueNo(queNo);
                optionVO.setCeId(ceId);
                optionVO.setOptionContent(optContent);
                examParsingMapper.insertOption(optionVO);
                optIdx++;
            }
        }
    }

    // -------------------------------
    // 보조 메서드들
    // -------------------------------
    private String generateCeId() {
        // DB에서 현재 가장 큰 CE_ID 조회 (예: "CE012")
        String lastCeId = examParsingMapper.getLastCeId(); 
        
        if (lastCeId == null) {
            return "CE001"; // DB에 아무 데이터가 없으면 첫 시험 ID는 CE001
        }

        // 숫자 부분만 추출
        int num = Integer.parseInt(lastCeId.replace("CE", ""));
        num++;

        // 다시 CE + 3자리 형식으로 변환
        return String.format("CE%03d", num);  // 예: CE013
    }

    private String generateQueNo(int questionNumber) {
        return String.format("Q%03d", questionNumber); // ex) Q001, Q002
    }

    private String generateOptNo(int optIdx) {
        return String.format("Opt%02d", optIdx); // ex) Opt01, Opt02
    }

    private String extractYearFromFilename(String filename) {
        // 파일명에서 "2021" 같은 연도를 추출하는 단순 로직
        return filename.replaceAll("[^0-9]", "").substring(0, 4);
    }
    
    private int generateCeRound() {
        Integer lastRound = examParsingMapper.getLastCeRound();
        if (lastRound == null) {
            return 1; // 첫 회차
        }
        return lastRound + 1;
    }

}
