import calendar
import sqlite3
from datetime import datetime

# SSMS(MSSQL) 연결용 라이브러리
import pyodbc

from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput


class ReceivingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. 전체 가상 캔버스 배경 설정
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # 메인 최외곽 레이아웃 프레임 구조
        main_layout = BoxLayout(orientation='vertical', padding=5, spacing=5)

        # 2. 메인 테마 타이틀 상단 바
        title_bar = Label(
            text="입고 등록", font_size='24sp', bold=True,
            size_hint_y=0.08, color=(1, 1, 1, 1)
        )
        with title_bar.canvas.before:
            Color(0.05, 0.45, 0.8, 1)
            self.t_rect = Rectangle(size=title_bar.size, pos=title_bar.pos)
        title_bar.bind(size=self._update_t_rect, pos=self._update_t_rect)
        main_layout.add_widget(title_bar)

        # 3. 상단 입력 정보 영역 (Grid)
        input_area = GridLayout(cols=4, spacing=10, padding=10)
        input_area.size_hint_y = None   
        input_area.height = 90          
        
        input_area.add_widget(Label(text="발주월", color=(0,0,0,1), size_hint_x=0.15, size_hint_y=None, height=30))
        self.btn_month = Button(text=datetime.now().strftime("%Y-%m"), background_normal='', background_color=(1,1,1,1), color=(0,0,0,1), size_hint_y=None, height=30)
        self.btn_month.bind(on_press=self.show_month_picker)
        input_area.add_widget(self.btn_month)

        input_area.add_widget(Label(text="입고일", color=(0,0,0,1), size_hint_x=0.15, size_hint_y=None, height=30))
        self.btn_date = Button(text=datetime.now().strftime("%Y-%m-%d"), background_normal='', background_color=(1,1,1,1), color=(0,0,0,1), size_hint_y=None, height=30)
        self.btn_date.bind(on_press=self.show_calendar)
        input_area.add_widget(self.btn_date)

        input_area.add_widget(Label(text="입고창고", color=(0,0,0,1), size_hint_y=None, height=30))
        self.btn_wh = Button(text="선택", background_normal='', background_color=(1,1,1,1), color=(0.3,0.3,0.3,1), size_hint_y=None, height=30)
        self.btn_wh.bind(on_press=lambda x: self.show_search_popup("입고창고 조회"))
        input_area.add_widget(self.btn_wh)

        input_area.add_widget(Label(text="거래처", color=(0,0,0,1), size_hint_y=None, height=30))
        self.btn_vendor = Button(text="선택", background_normal='', background_color=(1,1,1,1), color=(0.3,0.3,0.3,1), size_hint_y=None, height=30)
        self.btn_vendor.bind(on_press=lambda x: self.show_search_popup("거래처 조회"))
        input_area.add_widget(self.btn_vendor)
        
        main_layout.add_widget(input_area)

        # 4. 데이터 리스트 영역 1 (대용량 조회 시 느려지는 무거운 ScrollView 방식)
        main_layout.add_widget(Label(text="[ 발주 품목 리스트 ]", size_hint_y=0.05, color=(0.1, 0.1, 0.1, 1), font_size='14sp'))
        
        self.list_view_1 = ScrollView(size_hint_y=0.25)
        with self.list_view_1.canvas.before:
            Color(1, 1, 1, 1) 
            self.lv1_rect = Rectangle(size=self.list_view_1.size, pos=self.list_view_1.pos)
        self.list_view_1.bind(size=self._update_lv1_rect, pos=self._update_lv1_rect)
        
        # 내부 일반 그리드 레이아웃 (세로 높이가 들어오는 데이터만큼 무한정 늘어남)
        self.grid_items_1 = GridLayout(cols=5, spacing=1, size_hint_y=None)
        self.grid_items_1.bind(minimum_height=self.grid_items_1.setter('height'))
        
        self.list_view_1.add_widget(self.grid_items_1)
        main_layout.add_widget(self.list_view_1)

        # 5. 중간 버튼 제어 바 (조회 / 삭제)
        mid_bar = BoxLayout(size_hint_y=0.08, spacing=10, padding=5)
        btn_search = Button(text="조회", background_normal='', background_color=(0.4, 0.6, 0, 1), bold=True)
        btn_search.bind(on_release=self.fetch_db_order_items) 
        
        btn_delete = Button(text="삭제", background_normal='', background_color=(0.8, 0.2, 0.2, 1), bold=True)
        mid_bar.add_widget(btn_search)
        mid_bar.add_widget(btn_delete)
        main_layout.add_widget(mid_bar)

        # 6. 데이터 리스트 영역 2 (스캔된 내역)
        main_layout.add_widget(Label(text="[ 스캔 내역 ]", size_hint_y=0.05, color=(0.1, 0.1, 0.1, 1), font_size='14sp'))
        self.list_view_2 = BoxLayout(orientation='vertical', size_hint_y=0.25)
        with self.list_view_2.canvas.before:
            Color(1, 1, 1, 1)
            self.lv2_rect = Rectangle(size=self.list_view_2.size, pos=self.lv2_rect.pos if hasattr(self, 'lv2_rect') else [0,0])
        self.list_view_2.bind(size=self._update_lv2_rect, pos=self._update_lv2_rect)
        main_layout.add_widget(self.list_view_2)

        # 7. 하단 네비게이션 제어 바 시스템
        nav_bar = BoxLayout(size_hint_y=0.1, spacing=5, padding=5)
        nav_bar.add_widget(Button(text="다음", background_color=(0.1, 0.5, 0.8, 1)))
        btn_home = Button(text="홈", background_color=(0.1, 0.5, 0.8, 1))
        btn_home.bind(on_press=self.go_home)
        nav_bar.add_widget(btn_home)
        nav_bar.add_widget(Button(text="취소", background_color=(0.1, 0.5, 0.8, 1)))
        main_layout.add_widget(nav_bar)

        self.add_widget(main_layout)

    def fetch_db_order_items(self, instance):
        """조회 버튼 핸들러: SSMS 원본 커넥션 수립 후 데이터 로드"""
        try:
            conn_str = (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=localhost;"
                "Database=SHTECH_DB_TEST;" 
                "Trusted_Connection=yes;"
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            query = "SELECT ITEM_CODE, ITEM_NAME, QNTY_CODE, IPGO_QNTY, STAT_TYPE FROM BE_ITEM_INFO"
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            print(f"디버깅 로그 - 조회된 데이터 총 개수: {len(rows)}개")
            
            # 무거운 위젯 생성 함수 작동
            self.load_order_items(rows)
            
        except Exception as e:
            error_popup = Popup(
                title="데이터 조회 오류", 
                content=Label(text=f"접속 실패:\n{str(e)}", font_size='12sp'), 
                size_hint=(0.8, 0.4)
            )
            error_popup.open()

    def load_order_items(self, items_data):
        """🐢 [속도 저하 주범] 호출될 때마다 수천 개의 위젯을 실시간 add_widget하는 방식"""
        self.grid_items_1.clear_widgets()
        
        # 1. 표 헤더 생성
        headers = ["품목코드", "품목명", "규격", "발주량", "상태"]
        for h in headers:
            header_cell = BoxLayout(size_hint_y=None, height=35)
            with header_cell.canvas.before:
                Color(0.2, 0.5, 0.8, 1)
                rect = Rectangle(size=header_cell.size, pos=header_cell.pos)
            header_cell.bind(size=self._update_cell_rect, pos=self._update_cell_rect)
            header_cell.add_widget(Label(text=h, color=(1,1,1,1), bold=True, font_size='13sp'))
            self.grid_items_1.add_widget(header_cell)
            
        # 2. 데이터 행 실시간 위젯 생성 (1,000줄이면 5,000개 객체 순회 생성하느라 렉 발생)
        if items_data:
            for row_idx, item in enumerate(items_data):
                bg_color = [0.92, 0.94, 0.96, 1] if row_idx % 2 == 0 else [1, 1, 1, 1]
                for field in item:
                    cell = BoxLayout(size_hint_y=None, height=35)
                    with cell.canvas.before:
                        Color(*bg_color)
                        rect = Rectangle(size=cell.size, pos=cell.pos)
                    cell.bind(size=self._update_cell_rect, pos=self._update_cell_rect)
                    cell.add_widget(Label(text=str(field), color=(0,0,0,1), font_size='12sp'))
                    self.grid_items_1.add_widget(cell)

    def _update_cell_rect(self, instance, value):
        if instance.canvas.before.children:
            for child in instance.canvas.before.children:
                if isinstance(child, Rectangle):
                    child.pos = instance.pos
                    child.size = instance.size

    # --- 기존 달력 및 선택 팝업 시스템 유지 ---
    def show_calendar(self, instance):
        try: current_date = datetime.strptime(self.btn_date.text, "%Y-%m-%d")
        except: current_date = datetime.now()
        self.cal_year, self.cal_month = current_date.year, current_date.month
        self.cal_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.popup = Popup(title="입고일 선택", content=self.cal_layout, size_hint=(0.85, 0.65))
        self._render_custom_calendar()
        self.popup.open()

    def _render_custom_calendar(self):
        self.cal_layout.clear_widgets()
        header_bar = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10)
        btn_prev = Button(text="<", size_hint_x=0.2, background_color=(0.2, 0.5, 0.8, 1))
        btn_prev.bind(on_release=lambda x: self._change_cal_month(-1))
        lbl_month = Label(text=f"{self.cal_year}년 {self.cal_month}월", color=(1, 1, 1, 1), bold=True, font_size='16sp')
        btn_next = Button(text=">", size_hint_x=0.2, background_color=(0.2, 0.5, 0.8, 1))
        btn_next.bind(on_release=lambda x: self._change_cal_month(1))
        header_bar.add_widget(btn_prev); header_bar.add_widget(lbl_month); header_bar.add_widget(btn_next)
        self.cal_layout.add_widget(header_bar)
        
        day_bar = GridLayout(cols=7, size_hint_y=0.1)
        for w in ["일", "월", "화", "수", "목", "금", "토"]:
            c = (0.8, 0.2, 0.2, 1) if w == "일" else ((0.2, 0.5, 0.8, 1) if w == "토" else (0.7, 0.7, 0.7, 1))
            day_bar.add_widget(Label(text=w, color=c, font_size='12sp'))
        self.cal_layout.add_widget(day_bar)
        
        grid = GridLayout(cols=7, spacing=3, size_hint_y=0.7)
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.cal_year, self.cal_month)
        for week in month_days:
            for day in week:
                if day == 0: grid.add_widget(Label(text=""))
                else:
                    d_btn = Button(text=str(day), background_normal='', background_color=(1, 1, 1, 1), color=(0, 0, 0, 1))
                    if f"{self.cal_year}-{self.cal_month:02d}-{day:02d}" == self.btn_date.text:
                        d_btn.background_color = (0.1, 0.5, 0.8, 1); d_btn.color = (1, 1, 1, 1)
                    d_btn.bind(on_release=lambda btn, d=day: self._set_text_and_close(self.btn_date, f"{self.cal_year}-{self.cal_month:02d}-{int(btn.text):02d}"))
                    grid.add_widget(d_btn)
        for _ in range(len(month_days) * 7, 42): grid.add_widget(Label(text=""))
        self.cal_layout.add_widget(grid)

    def _change_cal_month(self, direction):
        self.cal_month += direction
        if self.cal_month < 1: self.cal_month = 12; self.cal_year -= 1
        elif self.cal_month > 12: self.cal_month = 1; self.cal_year += 1
        self._render_custom_calendar()

    def show_month_picker(self, instance):
        try: self.m_cal_year = datetime.strptime(self.btn_month.text, "%Y-%m").year
        except: self.m_cal_year = datetime.now().year
        self.month_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.popup = Popup(title="발주월 선택", content=self.month_layout, size_hint=(0.85, 0.55))
        self._render_custom_month_picker()
        self.popup.open()

    def _render_custom_month_picker(self):
        self.month_layout.clear_widgets()
        header_bar = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)
        btn_prev = Button(text="<", size_hint_x=0.2, background_color=(0.2, 0.5, 0.8, 1))
        btn_prev.bind(on_release=lambda x: self._change_month_year(-1))
        lbl_year = Label(text=f"{self.m_cal_year}년", color=(1, 1, 1, 1), bold=True, font_size='18sp')
        btn_next = Button(text=">", size_hint_x=0.2, background_color=(0.2, 0.5, 0.8, 1))
        btn_next.bind(on_release=lambda x: self._change_month_year(1))
        header_bar.add_widget(btn_prev); header_bar.add_widget(lbl_year); header_bar.add_widget(btn_next)
        self.month_layout.add_widget(header_bar)
        
        grid = GridLayout(cols=3, spacing=8, size_hint_y=0.75)
        for i in range(1, 13):
            m_str = f"{i:02d}"
            m_btn = Button(text=f"{i}월", background_normal='', background_color=(1, 1, 1, 1), color=(0, 0, 0, 1))
            if f"{self.m_cal_year}-{m_str}" == self.btn_month.text:
                m_btn.background_color = (0.1, 0.5, 0.8, 1); m_btn.color = (1, 1, 1, 1)
            m_btn.bind(on_release=lambda btn, m=m_str: self._set_text_and_close(self.btn_month, f"{self.m_cal_year}-{m}"))
            grid.add_widget(m_btn)
        self.month_layout.add_widget(grid)

    def _change_month_year(self, direction):
        self.m_cal_year += direction
        self._render_custom_month_picker()

    def show_search_popup(self, title):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        search_input = TextInput(hint_text="검색어 입력...", size_hint_y=0.2, multiline=False)
        dummy_list = Button(text="조회 결과: A-001 (클릭시 선택)", size_hint_y=0.6)
        target = self.btn_wh if "창고" in title else self.btn_vendor
        dummy_list.bind(on_release=lambda btn: self._set_text_and_close(target, "A-001"))
        layout.add_widget(search_input); layout.add_widget(dummy_list)
        self.popup = Popup(title=title, content=layout, size_hint=(0.8, 0.5))
        self.popup.open()

    def _set_text_and_close(self, target_widget, text):
        target_widget.text = text
        self.popup.dismiss()

    def go_home(self, instance): self.manager.current = 'main_menu'
    def _update_rect(self, instance, value): self.rect.pos = instance.pos; self.rect.size = instance.size
    def _update_t_rect(self, instance, value): self.t_rect.pos = instance.pos; self.t_rect.size = instance.size
    def _update_lv1_rect(self, instance, value): self.lv1_rect.pos = instance.pos; self.lv1_rect.size = instance.size
    def _update_lv2_rect(self, instance, value): self.lv2_rect.pos = instance.pos; self.lv2_rect.size = instance.size
