from information_processing_exam_parser import InformationProcessingExamParser
import sys
import os

pdf_path = sys.argv[1]
pdf_path = os.path.abspath(pdf_path)  # 절대 경로로 변환
pdf_path = pdf_path.replace("/", "\\")  # Windows용 백슬래시

try:
    # PDF 파일 열기
    parser = InformationProcessingExamParser(pdf_path)
    parser.open_pdf()  # PDF 파일 열기 추가
    
    if not parser.doc:
        print("PDF 파일을 열 수 없습니다.")
    
    print(f"📄 PDF 파일 로드 완료: 총 {len(parser.doc)} 페이지")
    
    # 1단계: 모든 좌표 정보 추출
    print("🔍 1단계: 좌표 정보 추출 중...")
    all_coordinates = parser.extract_all_coordinates()
    
    # 2단계: 문제 파싱
    print("📝 2단계: 문제 파싱 중...")
    all_questions_answers = parser.parse_all_questions(top_margin=0.05, bottom_margin=0.03)
    
    # 결과 출력
    print(f"\n✅ 파싱 완료: 총 {len(all_questions_answers)}개 문제")
    print(f"💾 결과 저장: {parser.output_dir / 'information_processing_parsed_questions.json'}")
    
    # 핵심 통계 출력
    if all_questions_answers:
        print(f"\n📊 파싱 통계:")
        
        # 과목별 문제 수
        subject_counts = {}
        for q in all_questions_answers:
            subject = q['subject']
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        for subject, count in subject_counts.items():
            print(f"  📖 {subject}: {count}개 문제")
        
        # 보기 개수 통계
        option_counts = {}
        for q in all_questions_answers:
            option_count = len(q['options'])
            option_counts[option_count] = option_counts.get(option_count, 0) + 1
        
        print(f"\n🔢 보기 개수 분포:")
        for count, num_questions in sorted(option_counts.items()):
            print(f"  {count}개 보기: {num_questions}개 문제")
        
        # 이미지가 있는 문제 수
        image_questions = [q for q in all_questions_answers if q.get('image_path')]
        print(f"\n🖼️ 이미지 문제: {len(image_questions)}개")
        
        # 보기 4개가 정확한 문제 수
        correct_option_questions = [q for q in all_questions_answers if len(q['options']) == 4]
        print(f"✅ 정확한 보기(4개): {len(correct_option_questions)}개")
        
        if len(correct_option_questions) != len(all_questions_answers):
            print(f"⚠️ 보기 부족 문제: {len(all_questions_answers) - len(correct_option_questions)}개")
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'parser' in locals():
        parser.close_pdf()