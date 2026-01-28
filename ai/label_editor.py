"""
OCR 라벨 에디터 GUI
마스킹 영역과 텍스트 위치를 시각적으로 드래그하여 조절하고 저장할 수 있는 도구

기능:
- 드래그로 영역 설정
- 이미지 생성 개수 설정
- 마스킹 효과 (색상 채우기)
- 흐림 효과 (Gaussian Blur)
- 모자이크 효과
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter
import subprocess
import threading


# 기본 설정 파일 경로
CONFIG_FILE = Path(__file__).parent / "label_config.json"

# 기본 필드 정의
DEFAULT_FIELDS = {
    'tracking_number': {
        'name': '운송장번호',
        'mask': [25, 65, 460, 230],
        'text': [35, 115, 440, 210],
        'font_size': 75,
    },
    'region_code': {
        'name': '지역코드',
        'mask': [890, 60, 1280, 240],
        'text': [905, 90, 1265, 220],
        'font_size': 110,
    },
    'recipient_name': {
        'name': '수신자명',
        'mask': [50, 235, 600, 380],
        'text': [60, 270, 580, 365],
        'font_size': 80,
    },
    'recipient_address': {
        'name': '수신자주소',
        'mask': [10, 330, 1275, 510],
        'text': [20, 380, 1260, 490],
        'font_size': 68,
    },
    'sender_name': {
        'name': '발신자명',
        'mask': [70, 475, 600, 630],
        'text': [80, 520, 580, 615],
        'font_size': 68,
    },
    'sender_address': {
        'name': '발신자주소',
        'mask': [10, 580, 1275, 860],
        'text': [20, 660, 1260, 760],
        'font_size': 68,
    },
}


class LabelEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR 라벨 에디터 - 드래그로 영역 설정")
        self.root.geometry("1550x1000")
        
        # 이미지 관련
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.photo_image = None
        self.scale = 1.0
        
        # 필드 설정
        self.fields = self.load_config()
        self.current_field = None
        self.edit_mode = 'mask'  # 'mask' or 'text'
        
        # 드래그 관련
        self.dragging = False
        self.drag_type = None
        self.drag_start = None
        self.drag_start_orig = None
        
        # 효과 미리보기용 이미지
        self.preview_effect_image = None
        
        self.setup_ui()
        self.load_default_image()
    
    def load_config(self):
        """설정 파일 로드"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    result = {}
                    for key, default_val in DEFAULT_FIELDS.items():
                        if key in loaded:
                            result[key] = {
                                'name': default_val['name'],
                                'mask': loaded[key].get('mask', default_val['mask']),
                                'text': loaded[key].get('text', default_val['text']),
                                'font_size': loaded[key].get('font_size', default_val['font_size']),
                            }
                        else:
                            result[key] = default_val.copy()
                    return result
            except:
                pass
        return {k: v.copy() for k, v in DEFAULT_FIELDS.items()}
    
    def save_config(self):
        """설정 파일 저장"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.fields, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("저장 완료", f"설정이 저장되었습니다.\n{CONFIG_FILE}")
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 왼쪽: 이미지 캔버스
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 상단 툴바
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="📂 이미지 불러오기", command=self.load_image).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="🔍+", command=lambda: self.zoom(1.2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔍-", command=lambda: self.zoom(0.8)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="1:1", command=lambda: self.set_scale(1.0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="맞춤", command=self.fit_to_window).pack(side=tk.LEFT, padx=2)
        
        self.scale_label = ttk.Label(toolbar, text="배율: 100%")
        self.scale_label.pack(side=tk.LEFT, padx=10)
        
        # 캔버스
        canvas_frame = ttk.Frame(left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#404040', cursor='crosshair')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(fill=tk.X)
        
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # 캔버스 이벤트
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        
        # 오른쪽: 컨트롤 패널
        right_frame = ttk.Frame(main_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # 노트북 (탭)
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # === 탭 1: 영역 설정 ===
        tab1 = ttk.Frame(notebook, padding=10)
        notebook.add(tab1, text="영역 설정")
        
        # 필드 선택
        field_frame = ttk.LabelFrame(tab1, text="1. 필드 선택", padding=10)
        field_frame.pack(fill=tk.X, pady=5)
        
        self.field_var = tk.StringVar()
        for key, data in self.fields.items():
            rb = ttk.Radiobutton(field_frame, text=f"{data['name']} ({key})", 
                               variable=self.field_var, value=key,
                               command=self.on_field_select)
            rb.pack(anchor=tk.W)
        
        # 편집 모드
        mode_frame = ttk.LabelFrame(tab1, text="2. 편집 모드", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.mode_var = tk.StringVar(value='mask')
        ttk.Radiobutton(mode_frame, text="마스킹 영역 (빨강)", 
                       variable=self.mode_var, value='mask',
                       command=self.on_mode_change).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="텍스트 위치 (파랑)", 
                       variable=self.mode_var, value='text',
                       command=self.on_mode_change).pack(anchor=tk.W)
        
        # 좌표 입력
        coord_frame = ttk.LabelFrame(tab1, text="좌표 (x1, y1, x2, y2)", padding=10)
        coord_frame.pack(fill=tk.X, pady=5)
        
        coord_grid = ttk.Frame(coord_frame)
        coord_grid.pack(fill=tk.X)
        
        self.coord_entries = []
        labels = ['x1:', 'y1:', 'x2:', 'y2:']
        for i, label in enumerate(labels):
            ttk.Label(coord_grid, text=label).grid(row=i//2, column=(i%2)*2, padx=2, sticky=tk.E)
            entry = ttk.Entry(coord_grid, width=10)
            entry.grid(row=i//2, column=(i%2)*2+1, padx=2, pady=2)
            self.coord_entries.append(entry)
        
        ttk.Button(coord_frame, text="좌표 적용", command=self.on_coord_change).pack(fill=tk.X, pady=(5, 0))
        
        # 폰트 크기
        font_frame = ttk.LabelFrame(tab1, text="폰트 크기", padding=10)
        font_frame.pack(fill=tk.X, pady=5)
        
        font_inner = ttk.Frame(font_frame)
        font_inner.pack(fill=tk.X)
        
        self.font_size_var = tk.StringVar(value='75')
        ttk.Entry(font_inner, textvariable=self.font_size_var, width=10).pack(side=tk.LEFT)
        ttk.Button(font_inner, text="적용", command=self.on_font_size_change).pack(side=tk.LEFT, padx=5)
        
        # 현재 설정
        info_frame = ttk.LabelFrame(tab1, text="현재 설정", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(info_frame, height=6, width=40, font=('Consolas', 9))
        self.info_text.pack(fill=tk.X)
        
        # === 탭 2: 이미지 효과 ===
        tab2 = ttk.Frame(notebook, padding=10)
        notebook.add(tab2, text="이미지 효과")
        
        # 효과 선택
        effect_frame = ttk.LabelFrame(tab2, text="효과 종류", padding=10)
        effect_frame.pack(fill=tk.X, pady=5)
        
        self.effect_var = tk.StringVar(value='none')
        effects = [
            ('none', '효과 없음 (기본)'),
            ('blur', '흐림 효과 (Gaussian Blur)'),
            ('mosaic', '모자이크 효과'),
            ('noise', '노이즈 추가'),
        ]
        for value, text in effects:
            ttk.Radiobutton(effect_frame, text=text, variable=self.effect_var, 
                          value=value, command=self.preview_effect).pack(anchor=tk.W)
        
        # 효과 강도
        strength_frame = ttk.LabelFrame(tab2, text="효과 강도", padding=10)
        strength_frame.pack(fill=tk.X, pady=5)
        
        self.effect_strength = tk.IntVar(value=5)
        ttk.Label(strength_frame, text="강도 (1-20):").pack(anchor=tk.W)
        strength_scale = ttk.Scale(strength_frame, from_=1, to=20, 
                                   variable=self.effect_strength, orient=tk.HORIZONTAL,
                                   command=lambda v: self.preview_effect())
        strength_scale.pack(fill=tk.X)
        
        self.strength_label = ttk.Label(strength_frame, text="현재: 5")
        self.strength_label.pack(anchor=tk.W)
        
        # 효과 적용 영역
        area_frame = ttk.LabelFrame(tab2, text="효과 적용 영역", padding=10)
        area_frame.pack(fill=tk.X, pady=5)
        
        self.effect_area_var = tk.StringVar(value='全体')
        ttk.Radiobutton(area_frame, text="전체 이미지", 
                       variable=self.effect_area_var, value='全体').pack(anchor=tk.W)
        ttk.Radiobutton(area_frame, text="마스킹 영역만", 
                       variable=self.effect_area_var, value='mask').pack(anchor=tk.W)
        
        ttk.Button(tab2, text="효과 미리보기", command=self.preview_effect).pack(fill=tk.X, pady=10)
        
        # === 탭 3: 이미지 생성 ===
        tab3 = ttk.Frame(notebook, padding=10)
        notebook.add(tab3, text="이미지 생성")
        
        # 생성 개수
        count_frame = ttk.LabelFrame(tab3, text="생성 설정", padding=10)
        count_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(count_frame, text="생성할 이미지 개수:").pack(anchor=tk.W)
        
        count_inner = ttk.Frame(count_frame)
        count_inner.pack(fill=tk.X, pady=5)
        
        self.count_var = tk.StringVar(value='100')
        count_entry = ttk.Entry(count_inner, textvariable=self.count_var, width=10)
        count_entry.pack(side=tk.LEFT)
        ttk.Label(count_inner, text="개").pack(side=tk.LEFT, padx=5)
        
        # 빠른 선택 버튼
        quick_frame = ttk.Frame(count_frame)
        quick_frame.pack(fill=tk.X, pady=5)
        for n in [10, 50, 100, 500, 1000]:
            ttk.Button(quick_frame, text=str(n), width=6,
                      command=lambda x=n: self.count_var.set(str(x))).pack(side=tk.LEFT, padx=2)
        
        # 출력 디렉토리
        ttk.Label(count_frame, text="\n출력 디렉토리:").pack(anchor=tk.W)
        
        output_inner = ttk.Frame(count_frame)
        output_inner.pack(fill=tk.X, pady=5)
        
        self.output_var = tk.StringVar(value='generated')
        ttk.Entry(output_inner, textvariable=self.output_var, width=25).pack(side=tk.LEFT)
        ttk.Button(output_inner, text="찾아보기", command=self.browse_output).pack(side=tk.LEFT, padx=5)
        
        # 생성 옵션
        option_frame = ttk.LabelFrame(tab3, text="생성 옵션", padding=10)
        option_frame.pack(fill=tk.X, pady=5)
        
        self.apply_effect_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(option_frame, text="이미지 효과 적용", 
                       variable=self.apply_effect_var).pack(anchor=tk.W)
        
        self.random_effect_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(option_frame, text="랜덤 효과 강도 (1~설정값)", 
                       variable=self.random_effect_var).pack(anchor=tk.W)
        
        # 생성 버튼
        generate_frame = ttk.Frame(tab3)
        generate_frame.pack(fill=tk.X, pady=20)
        
        self.generate_btn = ttk.Button(generate_frame, text="🚀 이미지 생성 시작", 
                                       command=self.start_generation)
        self.generate_btn.pack(fill=tk.X, pady=5)
        
        # 진행 상태
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(generate_frame, variable=self.progress_var, 
                                            maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(generate_frame, text="대기 중...")
        self.status_label.pack(anchor=tk.W)
        
        # === 하단 버튼 ===
        bottom_frame = ttk.Frame(right_frame)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(bottom_frame, text="💾 설정 저장", command=self.save_config).pack(fill=tk.X, pady=2)
        ttk.Button(bottom_frame, text="🔄 기본값 초기화", command=self.reset_to_default).pack(fill=tk.X, pady=2)
        
        # 첫 번째 필드 선택
        self.field_var.set('tracking_number')
        self.on_field_select()
    
    def load_default_image(self):
        """기본 이미지 로드"""
        default_path = Path(__file__).parent / "img" / "운송장 예시파일.jpg"
        if default_path.exists():
            self.load_image_file(str(default_path))
    
    def load_image(self):
        """이미지 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="이미지 선택",
            filetypes=[("이미지 파일", "*.jpg *.jpeg *.png *.bmp"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.load_image_file(file_path)
    
    def load_image_file(self, file_path):
        """이미지 파일 로드"""
        self.image_path = file_path
        self.original_image = Image.open(file_path)
        self.fit_to_window()
    
    def fit_to_window(self):
        """화면에 맞게 스케일 조정"""
        if self.original_image:
            self.scale = min(950 / self.original_image.width, 700 / self.original_image.height)
            self.update_display()
    
    def zoom(self, factor):
        """확대/축소"""
        self.scale = max(0.1, min(5.0, self.scale * factor))
        self.update_display()
    
    def set_scale(self, scale):
        """스케일 설정"""
        self.scale = scale
        self.update_display()
    
    def update_display(self):
        """화면 업데이트"""
        if self.original_image is None:
            return
        
        self.scale_label.config(text=f"배율: {int(self.scale * 100)}%")
        
        new_width = int(self.original_image.width * self.scale)
        new_height = int(self.original_image.height * self.scale)
        
        # 이미지 복사
        display_img = self.original_image.copy()
        draw = ImageDraw.Draw(display_img, 'RGBA')
        
        # 모든 필드 영역 그리기
        for field_key, field_data in self.fields.items():
            is_selected = (self.current_field == field_key)
            
            # 마스킹 영역 (빨강)
            mask = field_data['mask']
            if is_selected and self.mode_var.get() == 'mask':
                mask_color = (255, 0, 0, 100)
                mask_outline = (255, 0, 0)
                mask_width = 3
            else:
                mask_color = (255, 0, 0, 40)
                mask_outline = (255, 100, 100)
                mask_width = 1
            draw.rectangle(mask, fill=mask_color, outline=mask_outline, width=mask_width)
            
            # 텍스트 영역 (파랑)
            text = field_data['text']
            if is_selected and self.mode_var.get() == 'text':
                text_color = (0, 0, 255, 100)
                text_outline = (0, 0, 255)
                text_width = 3
            else:
                text_color = (0, 0, 255, 40)
                text_outline = (100, 100, 255)
                text_width = 1
            draw.rectangle(text, fill=text_color, outline=text_outline, width=text_width)
            
            # 필드명 표시
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 18)
            except:
                font = ImageFont.load_default()
            
            label_y = min(mask[1], text[1]) - 22
            label_color = (255, 0, 0) if is_selected else (150, 150, 150)
            draw.text((mask[0], label_y), field_data['name'], fill=label_color, font=font)
        
        # 리사이즈
        display_img = display_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.photo_image = ImageTk.PhotoImage(display_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image, tags="image")
        self.canvas.configure(scrollregion=(0, 0, new_width, new_height))
        
        self.update_info()
    
    def update_info(self):
        """정보 텍스트 업데이트"""
        self.info_text.delete(1.0, tk.END)
        
        if self.current_field and self.current_field in self.fields:
            field = self.fields[self.current_field]
            
            info = f"마스크: {field['mask']}\n"
            info += f"텍스트: {field['text']}\n"
            info += f"폰트: {field['font_size']}"
            self.info_text.insert(1.0, info)
            
            coords = field['mask'] if self.mode_var.get() == 'mask' else field['text']
            for i, entry in enumerate(self.coord_entries):
                entry.delete(0, tk.END)
                entry.insert(0, str(coords[i]))
            
            self.font_size_var.set(str(field['font_size']))
    
    def on_field_select(self, event=None):
        self.current_field = self.field_var.get()
        self.update_display()
    
    def on_mode_change(self):
        self.edit_mode = self.mode_var.get()
        self.update_display()
    
    def on_coord_change(self, event=None):
        if not self.current_field:
            return
        try:
            coords = [int(entry.get()) for entry in self.coord_entries]
            key = 'mask' if self.mode_var.get() == 'mask' else 'text'
            self.fields[self.current_field][key] = coords
            self.update_display()
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력하세요.")
    
    def on_font_size_change(self):
        if not self.current_field:
            return
        try:
            size = int(self.font_size_var.get())
            self.fields[self.current_field]['font_size'] = size
            self.update_info()
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력하세요.")
    
    def canvas_to_image_coords(self, x, y):
        return int(x / self.scale), int(y / self.scale)
    
    def get_handle_at(self, x, y):
        if not self.current_field:
            return None
        
        orig_x, orig_y = self.canvas_to_image_coords(x, y)
        
        key = 'mask' if self.mode_var.get() == 'mask' else 'text'
        rect = self.fields[self.current_field][key]
        x1, y1, x2, y2 = rect
        
        handle_size = 12 / self.scale
        
        if abs(orig_x - x1) < handle_size and abs(orig_y - y1) < handle_size:
            return 'resize_tl'
        if abs(orig_x - x2) < handle_size and abs(orig_y - y1) < handle_size:
            return 'resize_tr'
        if abs(orig_x - x1) < handle_size and abs(orig_y - y2) < handle_size:
            return 'resize_bl'
        if abs(orig_x - x2) < handle_size and abs(orig_y - y2) < handle_size:
            return 'resize_br'
        
        if abs(orig_x - x1) < handle_size and y1 < orig_y < y2:
            return 'resize_l'
        if abs(orig_x - x2) < handle_size and y1 < orig_y < y2:
            return 'resize_r'
        if abs(orig_y - y1) < handle_size and x1 < orig_x < x2:
            return 'resize_t'
        if abs(orig_y - y2) < handle_size and x1 < orig_x < x2:
            return 'resize_b'
        
        if x1 <= orig_x <= x2 and y1 <= orig_y <= y2:
            return 'move'
        
        return 'draw'
    
    def on_mouse_move(self, event):
        if not self.current_field:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        handle = self.get_handle_at(x, y)
        
        cursors = {
            'resize_tl': 'top_left_corner', 'resize_tr': 'top_right_corner',
            'resize_bl': 'bottom_left_corner', 'resize_br': 'bottom_right_corner',
            'resize_l': 'left_side', 'resize_r': 'right_side',
            'resize_t': 'top_side', 'resize_b': 'bottom_side',
            'move': 'fleur', 'draw': 'crosshair',
        }
        self.canvas.config(cursor=cursors.get(handle, 'crosshair'))
    
    def on_mouse_down(self, event):
        if not self.current_field:
            messagebox.showinfo("안내", "먼저 필드를 선택하세요.")
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        self.drag_type = self.get_handle_at(x, y)
        self.dragging = True
        self.drag_start = (x, y)
        self.drag_start_orig = self.canvas_to_image_coords(x, y)
        
        if self.drag_type == 'draw':
            key = 'mask' if self.mode_var.get() == 'mask' else 'text'
            orig_x, orig_y = self.drag_start_orig
            self.fields[self.current_field][key] = [orig_x, orig_y, orig_x, orig_y]
    
    def on_mouse_drag(self, event):
        if not self.dragging or not self.current_field:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        orig_x, orig_y = self.canvas_to_image_coords(x, y)
        
        key = 'mask' if self.mode_var.get() == 'mask' else 'text'
        rect = self.fields[self.current_field][key]
        x1, y1, x2, y2 = rect
        
        if self.drag_type == 'draw':
            start_x, start_y = self.drag_start_orig
            self.fields[self.current_field][key] = [
                min(start_x, orig_x), min(start_y, orig_y),
                max(start_x, orig_x), max(start_y, orig_y)
            ]
        elif self.drag_type == 'move':
            dx = orig_x - int(self.drag_start[0] / self.scale)
            dy = orig_y - int(self.drag_start[1] / self.scale)
            self.fields[self.current_field][key] = [x1 + dx, y1 + dy, x2 + dx, y2 + dy]
            self.drag_start = (x, y)
        elif self.drag_type == 'resize_tl':
            self.fields[self.current_field][key] = [orig_x, orig_y, x2, y2]
        elif self.drag_type == 'resize_tr':
            self.fields[self.current_field][key] = [x1, orig_y, orig_x, y2]
        elif self.drag_type == 'resize_bl':
            self.fields[self.current_field][key] = [orig_x, y1, x2, orig_y]
        elif self.drag_type == 'resize_br':
            self.fields[self.current_field][key] = [x1, y1, orig_x, orig_y]
        elif self.drag_type == 'resize_l':
            self.fields[self.current_field][key] = [orig_x, y1, x2, y2]
        elif self.drag_type == 'resize_r':
            self.fields[self.current_field][key] = [x1, y1, orig_x, y2]
        elif self.drag_type == 'resize_t':
            self.fields[self.current_field][key] = [x1, orig_y, x2, y2]
        elif self.drag_type == 'resize_b':
            self.fields[self.current_field][key] = [x1, y1, x2, orig_y]
        
        self.update_display()
    
    def on_mouse_up(self, event):
        if self.dragging and self.current_field:
            key = 'mask' if self.mode_var.get() == 'mask' else 'text'
            rect = self.fields[self.current_field][key]
            x1, y1, x2, y2 = rect
            self.fields[self.current_field][key] = [
                min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
            ]
            self.update_display()
        
        self.dragging = False
        self.drag_type = None
    
    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom(1.15)
        else:
            self.zoom(0.85)
    
    def preview_effect(self):
        """효과 미리보기"""
        if self.original_image is None:
            return
        
        self.strength_label.config(text=f"현재: {self.effect_strength.get()}")
        
        effect = self.effect_var.get()
        strength = self.effect_strength.get()
        
        if effect == 'none':
            self.update_display()
            return
        
        img = self.original_image.copy()
        
        if effect == 'blur':
            img = img.filter(ImageFilter.GaussianBlur(radius=strength))
        elif effect == 'mosaic':
            # 모자이크 효과
            small = img.resize((img.width // (strength + 1), img.height // (strength + 1)), 
                              Image.Resampling.BILINEAR)
            img = small.resize(img.size, Image.Resampling.NEAREST)
        elif effect == 'noise':
            # 노이즈 효과 (간단한 구현)
            import random
            pixels = img.load()
            for i in range(img.width):
                for j in range(img.height):
                    if random.random() < strength / 100:
                        r, g, b = pixels[i, j][:3]
                        noise = random.randint(-strength * 5, strength * 5)
                        pixels[i, j] = (
                            max(0, min(255, r + noise)),
                            max(0, min(255, g + noise)),
                            max(0, min(255, b + noise))
                        )
        
        # 영역 그리기
        draw = ImageDraw.Draw(img, 'RGBA')
        for field_key, field_data in self.fields.items():
            is_selected = (self.current_field == field_key)
            mask = field_data['mask']
            text = field_data['text']
            
            mask_color = (255, 0, 0, 100) if is_selected else (255, 0, 0, 40)
            text_color = (0, 0, 255, 100) if is_selected else (0, 0, 255, 40)
            
            draw.rectangle(mask, fill=mask_color, outline=(255, 0, 0), width=2 if is_selected else 1)
            draw.rectangle(text, fill=text_color, outline=(0, 0, 255), width=2 if is_selected else 1)
        
        # 리사이즈 및 표시
        new_width = int(img.width * self.scale)
        new_height = int(img.height * self.scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.photo_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
    
    def browse_output(self):
        """출력 디렉토리 선택"""
        dir_path = filedialog.askdirectory(title="출력 디렉토리 선택")
        if dir_path:
            self.output_var.set(dir_path)
    
    def start_generation(self):
        """이미지 생성 시작"""
        # 설정 저장
        self.save_config()
        
        try:
            count = int(self.count_var.get())
            if count < 1:
                raise ValueError()
        except:
            messagebox.showerror("오류", "올바른 생성 개수를 입력하세요.")
            return
        
        output_dir = self.output_var.get()
        
        # 버튼 비활성화
        self.generate_btn.config(state='disabled')
        self.progress_var.set(0)
        self.status_label.config(text="생성 중...")
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self.run_generation, args=(count, output_dir))
        thread.start()
    
    def run_generation(self, count, output_dir):
        """이미지 생성 실행 (별도 스레드)"""
        try:
            script_dir = Path(__file__).parent
            
            # 효과 설정 저장
            effect_config = {
                'apply_effect': self.apply_effect_var.get(),
                'effect_type': self.effect_var.get(),
                'effect_strength': self.effect_strength.get(),
                'random_strength': self.random_effect_var.get(),
            }
            
            effect_file = script_dir / 'effect_config.json'
            with open(effect_file, 'w') as f:
                json.dump(effect_config, f)
            
            # 프로세스 실행
            process = subprocess.Popen(
                ['python', 'generate_ocr_data.py', '-n', str(count), '-o', output_dir],
                cwd=script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 출력 읽기
            for line in process.stdout:
                if '진행률' in line or '%' in line:
                    try:
                        # "진행률: 50/100 (50.0%)" 형식 파싱
                        percent = float(line.split('(')[1].split('%')[0])
                        self.root.after(0, lambda p=percent: self.progress_var.set(p))
                        self.root.after(0, lambda l=line.strip(): self.status_label.config(text=l))
                    except:
                        pass
            
            process.wait()
            
            if process.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("완료", 
                    f"이미지 생성 완료!\n\n생성된 파일:\n{script_dir / output_dir}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("오류", "생성 중 오류가 발생했습니다."))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("오류", f"생성 실패: {e}"))
        
        finally:
            self.root.after(0, lambda: self.generate_btn.config(state='normal'))
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_label.config(text="완료"))
    
    def reset_to_default(self):
        """기본값으로 초기화"""
        if messagebox.askyesno("확인", "모든 설정을 기본값으로 초기화하시겠습니까?"):
            self.fields = {}
            for k, v in DEFAULT_FIELDS.items():
                self.fields[k] = {
                    'name': v['name'],
                    'mask': v['mask'].copy(),
                    'text': v['text'].copy(),
                    'font_size': v['font_size'],
                }
            self.update_display()


def main():
    root = tk.Tk()
    app = LabelEditor(root)
    root.mainloop()


if __name__ == '__main__':
    main()
