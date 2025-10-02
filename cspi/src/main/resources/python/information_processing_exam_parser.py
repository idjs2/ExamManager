import fitz  # PyMuPDF
import re
import json
import os
import hashlib  # hash / java에서 한글을 잘 못 읽어서 변환 작업
from pathlib import Path
from typing import List, Dict, Any

class InformationProcessingExamParser:
    """
    정보처리기사 시험 문제 PDF 파서
    
    기능:
    - PDF에서 문제 텍스트 추출
    - 문제 번호, 문제 내용, 보기 파싱
    - 과목별 분류 (1과목~5과목)
    - 개행 상태 유지
    - 머리말/꼬리말 제거
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.page_images = []  # 페이지별 이미지 정보
        self.current_text_blocks = []  # 현재 페이지의 텍스트 블록 정보
        
        # PDF 파일 이름을 기반으로 출력 폴더 생성
        self.pdf_name = Path(pdf_path).stem  # 확장자 제외한 파일명
        self.base_output_dir = Path(os.environ.get("PYTHON_OUTPUT_DIR", Path(pdf_path).parent.parent.parent.parent / "output"))
        
        self.hash_name = hashlib.md5(self.pdf_name.encode("utf-8")).hexdigest()[:8]
        self.output_dir = self.base_output_dir / f"output_{self.hash_name}"
        # self.output_dir = self.base_output_dir / f"output_{self.pdf_name}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 하위 폴더들 생성
        self.images_dir = self.output_dir / "extracted_images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 출력 폴더 생성: {self.output_dir}")
        print(f"📁 이미지 폴더 생성: {self.images_dir}")
        
        # 과목 구간 정보 (문제 번호 범위) - 실제 구조에 맞게 수정
        # PDF에서 실제로는 각 과목당 20문제씩이 아닐 수 있음
        self.subject_ranges = {
            "1과목": (1, 20),      # 1~20번
            "2과목": (21, 40),     # 21~40번
            "3과목": (41, 60),     # 41~60번
            "4과목": (61, 80),     # 61~80번
            "5과목": (81, 100)     # 81~100번
        }

        # 텍스트 정제/정답지 추출
        # -------------------------------------------------------------------------------------
        # ====== 정규식 패턴 ======
        self.HEADER_LINE = re.compile(r"(정보처리기사.*?CBT.*$|최강\s*자격증.*$|https?://\S+)", re.MULTILINE)
        self.SUBJECT_LINE = re.compile(r"^\s*\d+\s*과목\s*:\s*.*$", re.MULTILINE)  # 예: "1과목 : 소프트웨어 설계"
        self.PAGE_NUM_LINE = re.compile(r"^\s*\d+\s*$", re.MULTILINE)
        self.ANSWER_SHEET_MARK = re.compile(r"(전자문제집\s*CBT\s*PC\s*버전|기출문제\s*및\s*해설집\s*다운로드|정답\s*안내)", re.IGNORECASE)

        self.QUESTION_ANCHOR = re.compile(r"(?m)^\s*\d{1,3}\.\s")  # 문제 시작
        self.QUESTION_HEAD = re.compile(r"^(\d{1,3})\.\s*(.*)$", re.DOTALL)
        self.CHOICE_FINDER = re.compile(r"(?m)^\s*[①-④]\s")       # 보기 시작(①~④)
        
    def open_pdf(self):
        """PDF 파일을 엽니다."""
        try:
            self.doc = fitz.open(self.pdf_path)
            print(f"📄 PDF 파일 로드 완료: 총 {len(self.doc)} 페이지")
        except Exception as e:
            print(f"PDF 파일을 여는 중 오류 발생: {e}")


    # ====== 전처리 함수 ======
    def clean_page(self, text: str) -> str:
        """페이지 단위 클린업"""
        t = self.HEADER_LINE.sub("", text)      # 머리말/광고 제거
        t = self.SUBJECT_LINE.sub("", t)        # 과목 제목 제거
        t = self.PAGE_NUM_LINE.sub("", t)       # 페이지 번호 제거
        return t.strip()


    def heal_linebreaks(self, txt: str) -> str:
        """문장/단어 내부 줄바꿈 보정"""
        t = txt.replace("\r", "")
        # 문단 구분은 유지하기 위해 임시 토큰
        t = re.sub(r"\n{2,}", "¶¶", t)

        # 1) 단어 내부 끊김: 한글/영문 사이 개행 → 붙임
        t = re.sub(r"([가-힣A-Za-z])\s*\n\s*([가-힣A-Za-z])", r"\1\2", t)

        # 2) 문장 내부 개행 → 공백으로 치환 (단, 보기/새 문제/과목제목 시작 제외)
        t = re.sub(
            r"(?<![.!?:;)\]”’…])\n(?!\s*[①-④]|\s*\d{1,3}\.\s|\s*\d+\s*과목\s*:)",
            " ",
            t,
        )

        # 문단 복원
        t = t.replace("¶¶", "\n\n")
        return t


    def slice_questions(self, raw_text: str):
        """문제 단위로 자르기"""
        # 정답지 이후 컷
        m = self.ANSWER_SHEET_MARK.search(raw_text)
        if m:
            raw_text = raw_text[:m.start()]

        # 줄바꿈 보정
        raw_text = self.heal_linebreaks(raw_text)

        # 추가적으로 페이지 중간에 남아있는 머리말 제거
        raw_text = re.sub(r"정보처리기사\s*◐.*?CBT.*?\n", "", raw_text)
        raw_text = re.sub(r"최강\s*자격증.*?\n", "", raw_text)
        raw_text = re.sub(r"https?://\S+", "", raw_text)

        # 문제 단위 슬라이싱
        idxs = [m.start() for m in self.QUESTION_ANCHOR.finditer(raw_text)]
        idxs.append(len(raw_text))

        chunks = [raw_text[idxs[i]:idxs[i+1]].strip() for i in range(len(idxs)-1)]
        # 반드시 숫자. 로 시작하는 블록만 유지
        chunks = [c for c in chunks if re.match(r"^\d{1,3}\.\s", c)]
        return chunks


    def parse_question(self, chunk: str):
        """문제 번호, 지문, 보기 분리 (보기는 반드시 4개)"""
        m = self.QUESTION_HEAD.match(chunk)
        if not m:
            return None
        num = int(m.group(1))
        body = m.group(2).strip()

        # 1) '빈 보기' 패턴 제거 (문제 끝에 ①②③④만 나오는 경우)
        body = re.sub(r"\n\s*①\s*\n\s*②\s*\n\s*③\s*\n\s*④\s*", "", body)

        # 2) 보기 분리 (①②③④ 기준)
        parts = re.split(r"\s*[①②③④]\s*", body)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) >= 5:
            # [stem, opt1, opt2, opt3, opt4]
            stem, *opts = parts[:5]
            opts = opts[:4]
        else:
            stem = parts[0] if parts else body
            opts = []

        # 3) 보기 개수가 4개가 안 되면 빈칸으로 채우기
        while len(opts) < 4:
            opts.append("")

        stem = stem.replace("\n", " ").strip()
        opts = [o.replace("\n", " ").strip() for o in opts]

        return {"number": num, "stem": stem, "options": opts}
    

    def answers_parsing(self, txt_path) :
        with open(txt_path, "r", encoding="utf-8") as f :
            content = f.read()

        # 정답 text 뽑기
        split_content = content.split("오답 및 오탈자가 수정된 최신 자료와 해설은 전자문제집 CBT \n에서 확인하세요.")
        raw_answers_text = split_content[-1].split("=== 파싱 정보 ===")[0].strip()
        raw_answers_list = raw_answers_text.split("\n")

        # 정답 text >> 정답 list 뽑기
        ans_list = [raw for i, raw in enumerate(raw_answers_list) if i%20 > 9]

        # 정답 mapping
        answer_mapping = {'①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5}
        ans_map_list = [answer_mapping.get(ans, None) for ans in ans_list]

        # 문제-정답 매칭
        answers = {}
        for num, ans in enumerate(ans_map_list) :
            num += 1
            answers[num] = ans

        return answers
        # -------------------------------------------------------------------------------------

    def extract_text_from_region(self, page, problem_rect) -> str:
        """PDF 페이지에서 지정된 영역의 텍스트와 이미지 정보를 함께 추출합니다."""
        try:
            # 페이지별 이미지 정보 초기화
            self.page_images = []
            
            # 좌표 기반 텍스트와 이미지 정보 함께 추출
            extracted_content = self.extract_text_with_coordinates(page, problem_rect)
            
            # 이미지 정보 추출 (해당 페이지에서만) - 파일 저장용
            self.extract_image_info(page, problem_rect)
            
            # 77번 문제가 있는 페이지인지 확인 (디버깅용)
            if "77." in page.get_text():
                print(f"  🐛 페이지 {page.number}에서 77번 문제 발견!")
                print(f"  🐛 페이지 {page.number} 이미지 개수: {len(self.page_images)}")
                for i, img in enumerate(self.page_images):
                    print(f"  🐛 이미지 {i}: {img}")
            
            return extracted_content
        except Exception as e:
            print(f"텍스트와 이미지 추출 중 오류 발생: {e}")
            return ""
    
    def extract_image_info(self, page, problem_rect) -> List[dict]:
        """페이지에서 이미지 정보를 추출합니다."""
        image_info_list = []
        
        try:
            # 페이지의 전체 정보를 dict로 가져오기
            page_dict = page.get_text("dict")
            print(f"  🔍 페이지 {page.number}에서 {len(page_dict.get('blocks', []))}개 블록 발견")
            
            # 이미지 블록 찾기 (type == 1이 이미지 블록)
            image_blocks = []
            for block in page_dict.get("blocks", []):
                if block.get("type") == 1:  # 이미지 블록
                    image_blocks.append(block)
            
            print(f"  🔍 페이지 {page.number}에서 {len(image_blocks)}개 이미지 블록 발견")
            
            # 페이지의 모든 이미지 리스트 가져오기 (xref 정보용)
            page_images = page.get_images()
            print(f"  🔍 페이지 {page.number}에서 {len(page_images)}개 이미지 발견")
            
            for img_index, img_block in enumerate(image_blocks):
                try:
                    # 이미지 블록의 bbox 정보
                    bbox = img_block.get("bbox", [0, 0, 0, 0])
                    img_rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
                    
                    # 문제 영역과 겹치는지 확인
                    if img_rect.intersects(problem_rect):
                        # 이미지 데이터 추출 및 저장 (xref 사용)
                        img_path = self.extract_and_save_image_with_xref(page, page_images, img_index, bbox)
                        
                        if img_path:  # 성공적으로 저장된 경우만
                            # 이미지 정보 생성
                            image_info = {
                                'index': img_index,
                                'rect_index': 0,
                                'bbox': bbox,
                                'x': bbox[0],
                                'y': bbox[1],
                                'width': bbox[2] - bbox[0],
                                'height': bbox[3] - bbox[1],
                                'path': img_path
                            }
                            image_info_list.append(image_info)
                            print(f"  ✅ 이미지 {img_index} 저장됨: {img_path}")
                            print(f"     bbox: ({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})")
                    else:
                        # 영역과 겹치지 않아도 이미지는 저장
                        img_path = self.extract_and_save_image_with_xref(page, page_images, img_index, bbox)
                        if img_path:
                            print(f"  📄 이미지 {img_index} 저장됨 (영역 외부): {img_path}")
                                
                except Exception as e:
                    print(f"  ⚠️ 이미지 {img_index} 처리 중 오류: {e}")
                    continue
                    
        except Exception as e:
            print(f"  ❌ 이미지 추출 중 오류: {e}")
        
        return image_info_list
    

    def extract_and_save_image_with_xref(self, page, page_images, img_index: int, bbox) -> str:
        """
        xref를 사용하여 이미지를 추출하고 파일로 저장합니다.
        """
        try:
            # 이미지 저장 디렉토리는 이미 생성되어 있음 (self.images_dir)
            images_dir = str(self.images_dir)
            
            # 파일명 생성
            page_num = page.number
            
            # 페이지 이미지 리스트에서 해당 인덱스의 이미지 가져오기
            if img_index < len(page_images):
                img = page_images[img_index]
                img_xref = img[0]  # xref는 첫 번째 요소
                
                # 이미지 데이터 추출
                base_image = self.doc.extract_image(img_xref)
                image_ext = base_image["ext"]
                
                filename = f"page_{page_num}_img_{img_index}_0.{image_ext}"
                image_path = os.path.join(images_dir, filename)
                
                # 이미 파일이 존재하면 그 경로를 반환
                if os.path.exists(image_path):
                    return image_path
                
                # 이미지 파일 저장
                image_bytes = base_image["image"]
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                return image_path
            else:
                print(f"  ⚠️ 이미지 {img_index}: 페이지 이미지 리스트에 없음")
                return None
            
        except Exception as e:
            print(f"xref로 이미지 저장 중 오류: {e}")
            return None
    
    def extract_text_with_coordinates(self, page, problem_rect) -> str:
        """
        좌표 정보를 포함한 텍스트와 이미지를 단(段)을 고려하여 순서대로 추출합니다.
        """
        all_blocks = []
        
        # 페이지의 전체 정보를 dict로 가져오기
        page_dict = page.get_text("dict", clip=problem_rect)
        
        # 페이지의 모든 이미지 리스트 가져오기 (xref 정보용)
        page_images = page.get_images()
        
        # 텍스트 블록 처리
        for block in page_dict.get("blocks", []):
            if "lines" in block:  # 텍스트 블록
                for line in block["lines"]:
                    for span in line["spans"]:
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        # 텍스트 블록 정보 저장
                        all_blocks.append({
                            'type': 'text',
                            'text': span.get("text", ""),
                            'bbox': bbox,
                            'x': bbox[0],  # x 좌표 (단 구분용)
                            'y': bbox[1],  # y 좌표 (세로 위치)
                            'width': bbox[2] - bbox[0],  # 텍스트 너비
                            'height': bbox[3] - bbox[1]  # 텍스트 높이
                        })
            elif block.get("type") == 1:  # 이미지 블록
                bbox = block.get("bbox", [0, 0, 0, 0])
                
                # 이미지 파일 저장 및 경로 가져오기
                img_index = len([b for b in all_blocks if b['type'] == 'image'])
                img_path = self.extract_and_save_image_with_xref(page, page_images, img_index, bbox)
                
                # 이미지 블록 정보 저장 (실제 파일 경로 포함)
                relative_path = str(img_path).replace(str(self.images_dir), "extracted_images") if img_path else '저장실패'
                all_blocks.append({
                    'type': 'image',
                    'text': f"[이미지: {relative_path}]",
                    'bbox': bbox,
                    'x': bbox[0],
                    'y': bbox[1],
                    'width': bbox[2] - bbox[0],
                    'height': bbox[3] - bbox[1],
                    'image_id': block.get("image"),
                    'image_path': relative_path
                })
        
        # 현재 페이지의 텍스트 블록 정보 저장 (이미지 매칭용)
        self.current_text_blocks = [block for block in all_blocks if block['type'] == 'text']
        
        # 단(段)을 고려한 정렬 (텍스트와 이미지 모두 포함)
        sorted_content = self.sort_content_by_columns(all_blocks)
        
        return sorted_content
    
    
    def sort_content_by_columns(self, all_blocks: List[dict]) -> str:
        """
        단(段)을 고려하여 텍스트와 이미지를 함께 올바른 순서로 정렬합니다.
        """
        if not all_blocks:
            return ""
        
        # 텍스트 블록만 추출하여 단 경계 분석
        text_blocks = [block for block in all_blocks if block['type'] == 'text']
        
        # 문제 번호가 포함된 블록만을 기준으로 단 경계 분석
        question_blocks = []
        question_pattern = r'(\d+)\.'
        
        for block in text_blocks:
            if re.search(question_pattern, block['text']):
                # 1-100번 문제 번호만 고려
                matches = re.findall(question_pattern, block['text'])
                for match in matches:
                    if 1 <= int(match) <= 100:
                        question_blocks.append(block)
                        break
        
        # 문제 번호 블록의 x 좌표를 기준으로 단 경계 찾기
        if question_blocks:
            page_width = max([block['bbox'][2] for block in all_blocks])
            question_x_positions = [block['x'] for block in question_blocks]
            question_x_positions.sort()
            column_boundaries = self.find_column_boundaries(question_x_positions, page_width)
        else:
            # 문제 번호가 없으면 전체 블록으로 단 경계 찾기
            page_width = max([block['bbox'][2] for block in all_blocks])
            x_positions = [block['x'] for block in all_blocks]
            x_positions.sort()
            column_boundaries = self.find_column_boundaries(x_positions, page_width)
        
        # 단별로 모든 블록 분류 (텍스트와 이미지 모두)
        columns = {}
        for block in all_blocks:
            x = block['x']
            column = self.get_column_number(x, column_boundaries)
            
            if column not in columns:
                columns[column] = []
            columns[column].append(block)
        
        # 각 단 내에서 y 좌표 순으로 정렬
        for column in columns:
            columns[column].sort(key=lambda x: x['y'])
        
        # 단 순서대로 내용 결합
        result = ""
        column_order = sorted(columns.keys())  # 0번 단부터 순서대로
        
        # 디버깅: 단 구분 정보 출력
        print(f"  📄 단 구분: {len(columns)}개 단 발견 (텍스트+이미지)")
        for column in column_order:
            text_count = len([b for b in columns[column] if b['type'] == 'text'])
            image_count = len([b for b in columns[column] if b['type'] == 'image'])
            print(f"    단 {column}: 텍스트 {text_count}개, 이미지 {image_count}개")
        
        for column in column_order:
            for block in columns[column]:
                if block['type'] == 'text':
                    result += block['text'] + "\n"
                elif block['type'] == 'image':
                    # 이미지 블록의 실제 파일 경로 표시
                    result += block['text'] + "\n"
        
        return result

    
    def handle_image_options(self, options: List[str], option_images: Dict[str, List[str]] = None) -> List[str]:
        """
        이미지 기반 보기를 처리하여 실제 이미지 경로가 있으면 사용하고, 없으면 플레이스홀더를 사용합니다.
        """
        if len(options) < 2:  # 보기가 2개 미만이면 이미지 보기로 변경
            image_options = []
            option_symbols = ['①', '②', '③', '④', '⑤']
            
            for i in range(4):  # 기본적으로 4개 보기 생성
                symbol = option_symbols[i]
                if option_images and symbol in option_images:
                    # 실제 이미지 경로가 있으면 사용
                    image_paths = option_images[symbol]
                    if image_paths:
                        image_options.append(f"보기 {symbol} {image_paths[0]}")
                    else:
                        image_options.append(f"보기 {symbol}")
                else:
                    # 이미지 경로가 없으면 플레이스홀더 사용
                    image_options.append(f"보기 {symbol}")
            
            return image_options
        
        # 기존 보기가 있으면 이미지 경로 추가
        enhanced_options = []
        option_symbols = ['①', '②', '③', '④', '⑤']
        
        for i, option in enumerate(options):
            if i < len(option_symbols):
                symbol = option_symbols[i]
                if option_images and symbol in option_images:
                    # 해당 보기에 이미지가 있으면 경로만 추가
                    image_paths = option_images[symbol]
                    if image_paths:
                        enhanced_options.append(f"{option} {image_paths[0]}")
                    else:
                        enhanced_options.append(option)
                else:
                    enhanced_options.append(option)
            else:
                enhanced_options.append(option)
        
        return enhanced_options
        
    
    def process_question_images(self, question_number: int, start_pos: int, end_pos: int, subject_text: str):
        """
        문제의 이미지를 처리하여 문제 이미지와 보기 이미지로 분류합니다.
        bbox 기준 좌상단 좌표를 사용하여 거리 기반으로 매칭합니다.
        """
        question_images = []
        option_images = {}
        
        # 현재 페이지의 이미지 정보가 있는지 확인
        if not hasattr(self, 'page_images') or not self.page_images:
            return question_images, option_images
        
        print(f"  🔍 문제 {question_number}번 이미지 처리 시작")
        print(f"     페이지 이미지 개수: {len(self.page_images)}")
        
        # 문제 번호 block 찾기 (현재 문제에 해당하는 것만)
        question_block = None
        if hasattr(self, 'current_text_blocks'):
            for block in self.current_text_blocks:
                block_text = block.get('text', '')
                # 정확히 현재 문제 번호만 매칭
                if re.search(rf'\b{question_number}\.\s', block_text):
                    question_block = block
                    break
        
        # 보기 번호 block들 찾기 (현재 문제에 해당하는 것만)
        option_blocks = []
        if hasattr(self, 'current_text_blocks'):
            # 문제 텍스트에서 실제로 나타나는 보기만 찾기
            question_text_range = subject_text[start_pos:end_pos]
            found_options = re.findall(r'[①②③④⑤]', question_text_range)
            
            option_symbols = ['①', '②', '③', '④', '⑤']
            
            # 각 보기 번호별로 가장 가까운 블록 찾기
            for symbol in option_symbols:
                if symbol in found_options:
                    closest_block = None
                    min_distance = float('inf')
                    
                    for block in self.current_text_blocks:
                        block_text = block.get('text', '')
                        if symbol in block_text:
                            # 문제 번호와의 거리 계산
                            block_bbox = block.get('bbox', [0, 0, 0, 0])
                            block_center_x = (block_bbox[0] + block_bbox[2]) / 2
                            block_center_y = (block_bbox[1] + block_bbox[3]) / 2
                            
                            # 문제 번호 블록과의 거리 계산
                            if question_block:
                                q_bbox = question_block.get('bbox', [0, 0, 0, 0])
                                q_center_x = (q_bbox[0] + q_bbox[2]) / 2
                                q_center_y = (q_bbox[1] + q_bbox[3]) / 2
                                distance = ((block_center_x - q_center_x) ** 2 + (block_center_y - q_center_y) ** 2) ** 0.5
                                
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_block = block
                    
                    if closest_block:
                        bbox = closest_block.get('bbox', [0, 0, 0, 0])
                        option_blocks.append({
                            'option': symbol,
                            'text': closest_block.get('text', ''),
                            'bbox': bbox,
                            'center_x': (bbox[0] + bbox[2]) / 2,  # 중앙 x 좌표
                            'bottom_y': bbox[3]   # 하단 y 좌표
                        })
        
        print(f"     문제 블록: {'있음' if question_block else '없음'}")
        print(f"     보기 블록 개수: {len(option_blocks)}")
        
        # 77번 문제에 대해서만 상세 디버깅
        if question_number == 77:
            print(f"  🐛 77번 문제 이미지 매칭 상세 디버깅")
            if question_block:
                q_bbox = question_block.get('bbox', [0, 0, 0, 0])
                q_center_x = (q_bbox[0] + q_bbox[2]) / 2
                q_center_y = (q_bbox[1] + q_bbox[3]) / 2
                print(f"  🐛 문제 블록 중앙: ({q_center_x:.1f}, {q_center_y:.1f})")
                print(f"  🐛 문제 블록 텍스트: {question_block.get('text', '')[:50]}...")
            for opt in option_blocks:
                print(f"  🐛 보기 {opt['option']}: 중앙하단({opt['center_x']:.1f}, {opt['bottom_y']:.1f}) - '{opt['text'][:30]}...'")
        
        for i, img_info in enumerate(self.page_images):
            img_bbox = img_info.get('bbox')
            if not img_bbox:
                continue
            
            # 이미지 중앙 하단 좌표 (bbox 기준)
            img_center_x = (img_bbox[0] + img_bbox[2]) / 2  # 이미지 중앙 x 좌표
            img_bottom_y = img_bbox[3]  # 이미지 하단 y 좌표
            
            # 문제 번호와의 거리 계산 (중앙 좌표 기준)
            question_distance = float('inf')
            if question_block:
                q_bbox = question_block.get('bbox', [0, 0, 0, 0])
                q_center_x = (q_bbox[0] + q_bbox[2]) / 2  # 문제 중앙 x 좌표
                q_center_y = (q_bbox[1] + q_bbox[3]) / 2  # 문제 중앙 y 좌표
                question_distance = ((img_center_x - q_center_x) ** 2 + (img_bottom_y - q_center_y) ** 2) ** 0.5
            
            # 가장 가까운 보기 번호와의 거리 계산 (중앙 하단 좌표 기준)
            closest_option = None
            closest_option_distance = float('inf')
            
            for option_block in option_blocks:
                opt_center_x = option_block['center_x']  # 보기 중앙 x 좌표
                opt_bottom_y = option_block['bottom_y']  # 보기 하단 y 좌표
                distance = ((img_center_x - opt_center_x) ** 2 + (img_bottom_y - opt_bottom_y) ** 2) ** 0.5
                
                if distance < closest_option_distance:
                    closest_option_distance = distance
                    closest_option = option_block['option']
            
            if question_number == 77:
                print(f"  🐛 이미지 {i}: 중앙하단({img_center_x:.1f}, {img_bottom_y:.1f})")
                print(f"  🐛   문제 거리: {question_distance:.1f}")
                print(f"  🐛   가장 가까운 보기: {closest_option} (거리: {closest_option_distance:.1f})")
            
            # 문제 번호와 보기 번호 중 더 가까운 곳에 할당 (거리 임계값 200으로 조정)
            if question_distance < closest_option_distance and question_distance < 200:
                question_images.append(img_info['path'])
                if question_number == 77:
                    print(f"  🐛   → 문제 이미지로 분류")
            elif closest_option and closest_option_distance < 200:
                if closest_option not in option_images:
                    option_images[closest_option] = []
                option_images[closest_option].append(img_info['path'])
                if question_number == 77:
                    print(f"  🐛   → 보기 {closest_option}에 할당")
            elif question_number == 77:
                print(f"  🐛   → 거리가 너무 멀어서 할당하지 않음")
        
        print(f"     최종 결과: 문제 이미지 {len(question_images)}개, 보기 이미지 {len(option_images)}개")
        return question_images, option_images
            
    def find_closest_image_to_question(self, question_bbox: List[float], image_blocks: List[dict]) -> str:
        """
        문제 block의 중앙 좌표와 이미지 block의 중앙 하단 좌표를 비교하여 가장 가까운 이미지를 찾습니다.
        bbox 기준 중앙 하단 좌표를 사용하여 거리 기반으로 매칭합니다.
        """
        if not image_blocks:
            return None
        
        question_center_x = (question_bbox[0] + question_bbox[2]) / 2  # 문제 block 중앙 x 좌표
        question_center_y = (question_bbox[1] + question_bbox[3]) / 2  # 문제 block 중앙 y 좌표
        
        closest_image = None
        min_distance = float('inf')
        
        for img_info in image_blocks:
            img_bbox = img_info.get('bbox')
            if not img_bbox:
                continue
            
            # 이미지 block 중앙 하단 좌표
            img_center_x = (img_bbox[0] + img_bbox[2]) / 2  # 이미지 block 중앙 x 좌표
            img_bottom_y = img_bbox[3]  # 이미지 block 하단 y 좌표
            
            # 유클리드 거리 계산 (중앙 하단 좌표 기준)
            distance = ((question_center_x - img_center_x) ** 2 + (question_center_y - img_bottom_y) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_image = img_info.get('path')
        
        # 거리가 너무 멀면 (예: 150pt 이상) 매칭하지 않음 (임계값 조정)
        if min_distance > 150:
            return None
        
        return closest_image
        
    def find_column_boundaries(self, x_positions: List[float], page_width: float) -> List[float]:
        """
        x 좌표들을 분석하여 단 경계를 찾습니다.
        페이지 너비의 절반을 기준으로 단을 구분합니다.
        """
        # 페이지 너비의 절반을 기준으로 2단으로 나누기
        return [page_width / 2]
    
    def get_column_number(self, x: float, boundaries: List[float]) -> int:
        """
        x 좌표가 어느 단에 속하는지 판단합니다.
        """
        for i, boundary in enumerate(boundaries):
            if x < boundary:
                return i
        return len(boundaries)  # 마지막 단
    
    def extract_all_text_from_regions(self, top_margin: float = 0.05, bottom_margin: float = 0.01) -> str:
        """모든 페이지에서 텍스트와 이미지 정보를 함께 추출합니다."""
        if not self.doc:
            return ""
        
        all_text = ""
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_rect = page.rect
            
            # 페이지 크기
            page_width = page_rect.width
            page_height = page_rect.height
            
            # 머리말/꼬리말을 제외한 영역 계산
            top_y = page_height * top_margin
            bottom_y = page_height * (1 - bottom_margin)
            
            # 문제 영역만 추출
            problem_rect = fitz.Rect(0, top_y, page_width, bottom_y)
            
            # 텍스트와 이미지 정보를 함께 추출
            content = self.extract_text_from_region(page, problem_rect)
            
            # 페이지 구분자 추가
            all_text += f"\n=== 페이지 {page_num + 1} ===\n"
            all_text += content + "\n"
        
        return all_text
    
    def split_text_by_subjects(self, all_text: str) -> Dict[str, str]:
        """
        텍스트를 과목별로 나눕니다.
        """
        subject_sections = {}
        
        # 과목 구분자 패턴
        subject_pattern = r'(\d+과목\s*:\s*[^\n]+)'
        subject_matches = list(re.finditer(subject_pattern, all_text))
        
        if not subject_matches:
            # 과목 구분자가 없으면 전체를 1과목으로 처리
            subject_sections["1과목"] = all_text
            return subject_sections
        
        # 각 과목별 영역 추출
        for i, match in enumerate(subject_matches):
            subject_name = match.group(1).strip()
            start_pos = match.start()
            
            # 다음 과목 구분자 위치 찾기
            if i + 1 < len(subject_matches):
                end_pos = subject_matches[i + 1].start()
            else:
                # 마지막 과목인 경우
                end_pos = len(all_text)
            
            # 과목 영역 추출 (과목 구분자 포함)
            subject_text = all_text[start_pos:end_pos]
            subject_sections[subject_name] = subject_text
        
        return subject_sections
    
    def parse_questions_in_subject(self, subject_name: str, subject_text: str) -> List[Dict[str, Any]]:
        """
        특정 과목 내에서 문제들을 파싱합니다.
        """
        # 과목 구분자 제거
        clean_text = re.sub(r'^\d+과목\s*:\s*[^\n]+\n*', '', subject_text)
        
        # 해당 과목의 문제 번호들 찾기 (문제 번호 패턴: "1.", "2." 등)
        question_pattern = r'(\d+)\.'
        question_matches = re.findall(question_pattern, clean_text)
        unique_question_numbers = sorted(set([int(num) for num in question_matches if 1 <= int(num) <= 100]))
        
        print(f"  📖 {subject_name}: {len(unique_question_numbers)}개 문제")
        
        # 누락된 문제 번호 확인
        if unique_question_numbers:
            expected_range = range(min(unique_question_numbers), max(unique_question_numbers) + 1)
            missing_numbers = [num for num in expected_range if num not in unique_question_numbers]
            if missing_numbers:
                print(f"  ⚠️ {subject_name} 누락 문제: {missing_numbers}")
        
        questions = []
        for question_num in unique_question_numbers:
            question_data = self.parse_question_in_subject_text(clean_text, question_num, unique_question_numbers, subject_name)
            
            if question_data and len(question_data['options']) >= 2:
                questions.append(question_data)
            # else:
            #     print(f"  ⚠️ {subject_name} {question_num}번 문제 파싱 실패 또는 보기 부족")
        
        return questions
    
    def parse_question_in_subject_text(self, subject_text: str, question_number: int, all_question_numbers: List[int], subject_name: str) -> Dict[str, Any]:
        """
        과목 텍스트 내에서 특정 문제를 파싱합니다.
        """
        # 문제 번호 패턴 (예: "1.", "2." 등)
        question_pattern = rf'{question_number}\.'
        
        # 문제 번호 위치 찾기
        question_match = re.search(question_pattern, subject_text)
        if not question_match:
            return None
        
        start_pos = question_match.start()
        
        # 다음 문제 번호 위치 찾기
        next_question_num = question_number + 1
        if next_question_num in all_question_numbers:
            next_pattern = rf'{next_question_num}\.'
            next_match = re.search(next_pattern, subject_text[start_pos + 1:])
            if next_match:
                end_pos = start_pos + 1 + next_match.start()
            else:
                end_pos = len(subject_text)
        else:
            # 다음 문제 번호가 없으면 끝까지
            end_pos = len(subject_text)
        
        # 현재 문제 영역 추출
        question_text = subject_text[start_pos:end_pos]

        # 보기 찾기 (①②③④⑤) - 더 정확한 패턴
        options = []
        option_pattern = r'([①②③④⑤])\s*([^①②③④⑤\n]+(?:\n[^①②③④⑤\n]+)*)'
        option_matches = re.findall(option_pattern, question_text)

        # 보기가 부족하면 더 넓은 범위에서 찾기
        if len(option_matches) < 2:  # 최소 2개 보기는 있어야 함
            # 현재 문제 번호 이후부터 다음 문제 번호 이전까지의 모든 텍스트
            extended_text = subject_text[start_pos:end_pos]
            
            # 모든 보기 찾기
            all_options = re.findall(option_pattern, extended_text)
            
            # 현재 문제에 속하는 보기들만 필터링
            current_options = []
            for option_num, option_text in all_options:
                # 다음 문제 번호가 포함되어 있으면 중단
                if re.search(rf'\b{next_question_num}\b', option_text):
                    break
                # 과목 구분자가 포함되어 있으면 중단
                if re.search(r'\d+과목\s*:', option_text):
                    break
                current_options.append((option_num, option_text))
            
            option_matches = current_options
        
        # 보기가 여전히 부족한 경우 문제 영역 확장
        if len(option_matches) < 2:
            # 더 넓은 범위에서 보기 검색
            extended_search_range = max(200, len(question_text))
            extended_start = max(0, start_pos - extended_search_range)
            extended_end = min(len(subject_text), end_pos + extended_search_range)
            extended_text = subject_text[extended_start:extended_end]
            
            extended_options = re.findall(option_pattern, extended_text)
            if len(extended_options) > len(option_matches):
                option_matches = extended_options
        
        # 보기 순서 확인 및 정렬
        option_order = {'①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5}
        sorted_options = []
        for option_num, option_text in option_matches:
            if option_num in option_order:
                sorted_options.append((option_order[option_num], option_num, option_text))
        
        # 순서대로 정렬
        sorted_options.sort(key=lambda x: x[0])
        
        # 보기 정리 (정렬된 순서대로)
        for order, option_num, option_text in sorted_options:
            cleaned_option = re.sub(r'[ \t]+', ' ', option_text).strip()
            # [이미지: ...] 형태 제거
            cleaned_option = re.sub(r'\[이미지:[^\]]*\]', '', cleaned_option).strip()
            # [이미지 보기 ...] 형태 제거
            cleaned_option = re.sub(r'\[이미지 보기 [①②③④⑤]\]', '', cleaned_option).strip()
            # 전자문제집 CBT 관련 텍스트 제거
            cleaned_option = re.sub(r'전자문제집 CBT.*?확인하세요\.', '', cleaned_option, flags=re.DOTALL).strip()
            # 정답지 패턴 제거 (1, 2, 3, 4, 5... 형태의 숫자들)
            cleaned_option = re.sub(r'^\d+\s*\n\d+\s*\n\d+\s*\n\d+\s*\n\d+\s*\n\d+\s*\n\d+\s*\n\d+\s*\n\d+\s*\n\d+$', '', cleaned_option, flags=re.MULTILINE).strip()
            if cleaned_option:
                options.append(cleaned_option)

        # 보기 번호만 있고 내용이 없는 경우 처리
        if len(options) == 0 and len(sorted_options) > 0:
            # 보기 번호만 있는 경우, 이미지를 순서대로 매칭
            image_pattern = r'\[이미지:\s*([^\]]+)\]'
            image_matches = re.findall(image_pattern, question_text)
            
            if image_matches:
                # 이미지를 y 좌표 순서대로 정렬 (위에서 아래로)
                image_blocks = []
                for match in image_matches:
                    image_path = match.strip()
                    if 'extracted_images\\' in image_path:
                        # 이미지 파일명에서 페이지와 인덱스 추출
                        filename = image_path.split('extracted_images\\')[-1]
                        if 'page_' in filename and '_img_' in filename:
                            try:
                                # page_X_img_Y_0.png 형태에서 Y 추출
                                parts = filename.split('_img_')
                                if len(parts) == 2:
                                    img_index = int(parts[1].split('_')[0])
                                    image_blocks.append((img_index, image_path))
                            except:
                                image_blocks.append((999, image_path))  # 파싱 실패시 마지막에 배치
                        else:
                            image_blocks.append((999, image_path))
                    else:
                        image_blocks.append((999, image_path))
                
                # 이미지 인덱스 순서대로 정렬
                image_blocks.sort(key=lambda x: x[0])
                sorted_image_paths = [block[1] for block in image_blocks]
                
                # 보기 번호와 이미지 매칭
                option_symbols = ['①', '②', '③', '④', '⑤']
                for i, (order, option_num, option_text) in enumerate(sorted_options):
                    if i < len(sorted_image_paths):
                        # 해당 보기에 이미지 경로 추가
                        image_path = sorted_image_paths[i]
                        if 'extracted_images\\' in image_path:
                            path_only = image_path.split('extracted_images\\')[-1]
                            path_only = f"extracted_images\\{path_only}"
                            options.append(path_only)
                        else:
                            options.append("")
                    else:
                        options.append("")
            else:
                # 이미지가 없는 경우 빈 문자열 추가
                for order, option_num, option_text in sorted_options:
                    options.append("")

        # 이미지 정보 처리 (bbox 기준 좌상단 좌표로 매칭)
        question_images, option_images = self.process_question_images(question_number, start_pos, end_pos, subject_text)
        
        # 문제 내용 추출
        question_content = ""
        if sorted_options:
            first_option_start = question_text.find(sorted_options[0][1])  # 첫 번째 보기 번호
            if first_option_start != -1:
                question_content = question_text[:first_option_start].strip()
            else:
                question_content = question_text.strip()

            # 문제 번호 제거 ("1." 형태)
            question_content = re.sub(rf'^{question_number}\.\s*', '', question_content).strip()
        else:
            question_content = re.sub(rf'^{question_number}\.\s*', '', question_text).strip()
        
        # [이미지: ...] 부분 제거
        question_content = re.sub(r'\[이미지:[^\]]*\]', '', question_content).strip()
        
        # 전자문제집 CBT 관련 텍스트 제거 (마지막 페이지의 부가 정보)
        question_content = re.sub(r'전자문제집 CBT PC 버전\s*:.*?확인하세요\.', '', question_content, flags=re.DOTALL).strip()
        question_content = re.sub(r'전자문제집 CBT란\?.*?확인하세요\.', '', question_content, flags=re.DOTALL).strip()

        # 문제 block의 좌상단 좌표 찾기
        question_bbox = None
        if hasattr(self, 'current_text_blocks'):
            for block in self.current_text_blocks:
                if re.search(rf'\b{question_number}\.\s', block.get('text', '')):
                    question_bbox = block.get('bbox')
                    break
        
        # 가장 가까운 이미지 찾기 (문제 이미지용) - bbox 기준 좌상단 좌표로 매칭
        image_path = None
        if question_bbox and hasattr(self, 'page_images'):
            image_path = self.find_closest_image_to_question(question_bbox, self.page_images)
        
        # [이미지: 로 시작되는 텍스트가 있는지 확인하고 경로 추출
        image_path_from_text = None
        image_pattern = r'\[이미지:\s*([^\]]+)\]'
        image_matches = re.findall(image_pattern, question_text)
        if image_matches:
            # 첫 번째 이미지 경로 사용
            image_path_from_text = image_matches[0].strip()
            # 경로만 추출 (extracted_images\page_0_img_1_0.png 형태)
            if 'extracted_images\\' in image_path_from_text:
                image_path_from_text = image_path_from_text.split('extracted_images\\')[-1]
                image_path_from_text = f"extracted_images\\{image_path_from_text}"
        
        # 보기에 이미지 경로 추가 (bbox 기준 좌상단 좌표로 매칭된 결과 사용)
        if option_images:
            # option_images에 있는 보기들에 이미지 경로 추가
            enhanced_options = []
            option_symbols = ['①', '②', '③', '④', '⑤']
            
            for i, option in enumerate(options):
                if i < len(option_symbols):
                    symbol = option_symbols[i]
                    if symbol in option_images:
                        # 해당 보기에 이미지가 있으면 경로만 추가
                        image_paths = option_images[symbol]
                        if image_paths:
                            enhanced_options.append(f"{option} {image_paths[0]}")
                        else:
                            enhanced_options.append(option)
                    else:
                        enhanced_options.append(option)
                else:
                    enhanced_options.append(option)
            
            options = enhanced_options
        elif len(options) < 2:
            # 보기가 부족하고 이미지도 없으면 플레이스홀더 생성
            options = self.handle_image_options(options)
        
        # 추가: raw_parsed_text에서 [이미지: ...] 패턴을 찾아서 해당 보기에 추가
        # 문제 텍스트에서 보기별로 이미지 정보 찾기
        option_image_pattern = r'([①②③④⑤])\s*([^①②③④⑤\n]*?)\[이미지:\s*([^\]]+)\]([^①②③④⑤\n]*)'
        option_image_matches = re.findall(option_image_pattern, question_text)
        
        if option_image_matches:
            # 기존 options를 enhanced_options로 변환
            enhanced_options = options.copy()
            option_symbols = ['①', '②', '③', '④', '⑤']
            
            for option_symbol, before_text, image_path, after_text in option_image_matches:
                # 해당 보기 번호의 인덱스 찾기
                option_index = option_symbols.index(option_symbol) if option_symbol in option_symbols else -1
                
                if option_index >= 0 and option_index < len(enhanced_options):
                    # 해당 보기에 이미지 경로만 추가 (extracted_images\... 형태)
                    current_option = enhanced_options[option_index]
                    if 'extracted_images\\' not in current_option:  # 아직 이미지가 추가되지 않은 경우만
                        # 경로만 추출
                        if 'extracted_images\\' in image_path:
                            path_only = image_path.split('extracted_images\\')[-1]
                            path_only = f"extracted_images\\{path_only}"
                            enhanced_options[option_index] = f"{current_option} {path_only}"
            options = enhanced_options
        
        # option_type 생성 - 보기가 이미지인지 or 텍스트인지 확인
        # -------------------------------------------------------
        if "extracted_images\\" in options[0] :
            option_type = "image"
        else :
            option_type = "text"
        # -------------------------------------------------------
        # 결과 구성
        result = {
            'question_number': question_number,
            'subject': subject_name,
            'question_text': question_content,
            'options': options,
            'option_type' : option_type,
            'image_path': image_path_from_text if image_path_from_text else (image_path if image_path else "")  # 텍스트에서 추출한 이미지 경로 우선
        }
        
        # 문제 이미지가 있으면 추가 (bbox 기준 좌상단 좌표로 매칭된 결과)
        if question_images:
            result['image'] = question_images
        
        return result
    
    def parse_all_questions(self, top_margin: float = 0.05, bottom_margin: float = 0.01) -> List[Dict[str, Any]]:
        """모든 문제를 파싱합니다."""
        all_text = self.extract_all_text_from_regions(top_margin, bottom_margin)

        # 깔끔한 텍스트 추출을 위한 추가 방안
        # -------------------------------------------------------
        raw_text = ""
        for page in self.doc:
            raw_text += self.clean_page(page.get_text()) + "\n"

        questions_raw = self.slice_questions(raw_text)
        questions_list = [self.parse_question(q) for q in questions_raw]
        questions_list = [q for q in questions_list if q]  # None 제거
        # -------------------------------------------------------

        # 최초 파싱 결과를 txt 파일로 저장
        raw_text_path = self.output_dir / 'raw_parsed_text.txt'
        with open(raw_text_path, 'w', encoding='utf-8') as f:
            f.write("=== 최초 파싱된 원본 텍스트 ===\n")
            f.write(all_text)
            f.write("\n\n=== 파싱 정보 ===\n")
        
        # 1. 과목 구분자 먼저 찾기
        subject_pattern = r'(\d+과목\s*:\s*[^\n]+)'
        subject_matches = re.findall(subject_pattern, all_text)
        print(f"📚 발견된 과목: {len(subject_matches)}개")
        
        # 파싱 정보를 txt 파일에 추가
        with open(raw_text_path, 'a', encoding='utf-8') as f:
            f.write(f"발견된 과목 구분자: {subject_matches}\n")
        
        # 2. 과목별 영역 나누기
        subject_sections = self.split_text_by_subjects(all_text)
        
        # 3. 각 과목별로 문제 파싱
        all_questions = []
        for subject_name, subject_text in subject_sections.items():
            print(f"\n=== {subject_name} 파싱 중 ===")
            
            # 해당 과목의 문제 번호들 찾기
            subject_questions = self.parse_questions_in_subject(subject_name, subject_text)
            all_questions.extend(subject_questions)

        # 문제 번호 순으로 정렬
        all_questions.sort(key=lambda x: x['question_number'])

        # 오추출 감지/수정
        # -------------------------------------------------------
        print("all_questions : ", len(all_questions))
        print("questions_list : ", len(questions_list))

        err_cnt = 0
        q = 1
        while len(all_questions) != len(questions_list) :
            prev = all_questions[q-1]
            daum = all_questions[q]
            if prev['question_number'] == daum['question_number'] :
                all_questions.remove(daum)
                q -= 1
                err_cnt += 1
            q += 1
        if err_cnt != 0 :
            print(f"※ {err_cnt}개의 문제를 수정했습니다.")
        else :
            print("수정할 문제가 없습니다.")
        # -------------------------------------------------------

        # 깔끔한 텍스트로 대체
        # -------------------------------------------------------
        for n in range(len(all_questions)) :
            if all_questions[n]['option_type'] == 'text' :
                all_questions[n]['question_text'] = questions_list[n]['stem']
                all_questions[n]['options'] = questions_list[n]['options']
        # -------------------------------------------------------
        

        # 딕셔너리에 정답 추가
        all_questions_answers = []
        answers = self.answers_parsing(raw_text_path)

        for i, question in enumerate(all_questions) :
            num = i+1
            question['answer'] = answers[num]
            all_questions_answers.append(question)

        # JSON 파일로 저장
        try:
            json_path = self.output_dir / 'information_processing_parsed_questions.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_questions_answers, f, ensure_ascii=False, indent=2)
            print(f"\n총 파싱된 문제 수: {len(all_questions_answers)}")
            print(f"✅ 파싱 결과가 '{json_path}' 파일로 저장되었습니다.")
        except Exception as e:
            print(f"❌ JSON 파일 저장 중 오류 발생: {e}")
        
        return all_questions_answers
        
    def close_pdf(self):
        """PDF 파일을 닫습니다."""
        if self.doc:
            self.doc.close()

    def extract_all_coordinates(self):
        """모든 페이지의 이미지와 텍스트 block 좌표를 추출하여 파일로 저장합니다."""
        if not self.doc:
            return
        
        all_coordinates = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_rect = page.rect
            
            # print(f"📄 페이지 {page_num} 좌표 추출 중...")
            
            page_data = {
                'page_number': page_num,
                'page_width': page_rect.width,
                'page_height': page_rect.height,
                'text_blocks': [],
                'image_blocks': []
            }
            
            # 텍스트 block 좌표 추출
            try:
                text_dict = page.get_text("dict")
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text_block = {
                                    'text': span['text'],
                                    'bbox': span['bbox'],
                                    'x': span['bbox'][0],
                                    'y': span['bbox'][1],
                                    'width': span['bbox'][2] - span['bbox'][0],
                                    'height': span['bbox'][3] - span['bbox'][1],
                                    'font': span.get('font', ''),
                                    'size': span.get('size', 0)
                                }
                                page_data['text_blocks'].append(text_block)
            except Exception as e:
                print(f"  ⚠️ 페이지 {page_num} 텍스트 추출 오류: {e}")
            
            # 이미지 block 좌표 추출
            try:
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        # 이미지 정보
                        img_info = {
                            'index': img_index,
                            'xref': img[0],
                            'bbox': None,
                            'x': 0,
                            'y': 0,
                            'width': 0,
                            'height': 0
                        }
                        
                        # 이미지 바운딩 박스 시도 (여러 방법)
                        try:
                            img_rects = page.get_image_bbox(img)
                            if img_rects:
                                if isinstance(img_rects, list) and len(img_rects) > 0:
                                    img_rect = img_rects[0]
                                else:
                                    img_rect = img_rects
                                
                                img_info['bbox'] = [img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1]
                                img_info['x'] = img_rect.x0
                                img_info['y'] = img_rect.y0
                                img_info['width'] = img_rect.width
                                img_info['height'] = img_rect.height
                        except:
                            # 바운딩 박스를 가져올 수 없는 경우 기본값 사용
                            pass
                        
                        page_data['image_blocks'].append(img_info)
                        
                    except Exception as e:
                        print(f"  ⚠️ 페이지 {page_num} 이미지 {img_index} 처리 오류: {e}")
                        continue
                        
            except Exception as e:
                print(f"  ⚠️ 페이지 {page_num} 이미지 추출 오류: {e}")
            
            all_coordinates.append(page_data)
            # print(f"  ✅ 페이지 {page_num}: 텍스트 {len(page_data['text_blocks'])}개, 이미지 {len(page_data['image_blocks'])}개")
        
        # 파일로 저장
        coordinates_json_path = self.output_dir / 'all_coordinates.json'
        with open(coordinates_json_path, 'w', encoding='utf-8') as f:
            json.dump(all_coordinates, f, ensure_ascii=False, indent=2)
        
        # 보기 편한 텍스트 파일로도 저장
        coordinates_txt_path = self.output_dir / 'all_coordinates.txt'
        with open(coordinates_txt_path, 'w', encoding='utf-8') as f:
            f.write("=== 모든 페이지의 텍스트와 이미지 좌표 ===\n\n")
            
            for page_data in all_coordinates:
                f.write(f"📄 페이지 {page_data['page_number']} (크기: {page_data['page_width']:.1f} x {page_data['page_height']:.1f})\n")
                f.write("=" * 60 + "\n")
                
                # 텍스트 블록들
                f.write(f"\n📝 텍스트 블록 ({len(page_data['text_blocks'])}개):\n")
                f.write("-" * 40 + "\n")
                for i, block in enumerate(page_data['text_blocks']):
                    f.write(f"{i+1:3d}. 좌표({block['x']:6.1f}, {block['y']:6.1f}) 크기({block['width']:5.1f} x {block['height']:5.1f}) ")
                    f.write(f"폰트:{block['font'][:10]:10} 크기:{block['size']:4.1f} ")
                    f.write(f"텍스트: {block['text'][:50]}")
                    if len(block['text']) > 50:
                        f.write("...")
                    f.write("\n")
                
                # 이미지 블록들
                f.write(f"\n🖼️ 이미지 블록 ({len(page_data['image_blocks'])}개):\n")
                f.write("-" * 40 + "\n")
                for i, block in enumerate(page_data['image_blocks']):
                    f.write(f"{i+1:3d}. 인덱스:{block['index']:2d} xref:{block['xref']:4d} ")
                    if block['bbox']:
                        f.write(f"좌표({block['x']:6.1f}, {block['y']:6.1f}) 크기({block['width']:5.1f} x {block['height']:5.1f})")
                    else:
                        f.write("좌표 정보 없음")
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n\n")

        print(f"\n✅ 좌표 정보 저장 완료:")
        print(f"   - JSON: {self.output_dir / 'all_coordinates.json'}")
        print(f"   - 텍스트: {self.output_dir / 'all_coordinates.txt'}")
        
        
        return all_coordinates



def main(pdf_path):
    """메인 실행 함수"""
    try:
        # PDF 파일 열기
        parser = InformationProcessingExamParser(pdf_path)
        parser.open_pdf()  # PDF 파일 열기 추가
        
        if not parser.doc:
            print("PDF 파일을 열 수 없습니다.")
            return
        
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

if __name__ == "__main__":
    pdf_path = "C:/CSPI/Practice/python_extract/data/raw_data/infomation_processing/정보처리기사20220305(학생용).pdf"
    main(pdf_path)