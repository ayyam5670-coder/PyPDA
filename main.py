from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from screens.receiving import ReceivingScreen


# 1. 한글 폰트 설정 (맑은 고딕 경로)
KOREAN_FONT = "C:\\Windows\\Fonts\\malgun.ttf"
LabelBase.register(name="Roboto", fn_regular=KOREAN_FONT)

# PDA 해상도 느낌을 위해 윈도우 크기 고정 (테스트용)
Window.size = (450, 750)

# --- 각 기능별 화면 클래스 (예시) ---
class SubScreen(Screen):
    """모든 서브 화면의 공통 구조"""
    def __init__(self, title_text, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        layout.add_widget(Label(text=f"{title_text} 화면", font_size='30sp'))
        
        # 메인으로 돌아가는 버튼
        back_btn = Button(text="메인메뉴로 돌아가기", size_hint_y=0.2)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main_menu'

# --- 메인 메뉴 화면 클래스 ---
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. 배경색 설정 (도화지 깔기)
        with self.canvas.before:
            Color(0.92, 0.94, 0.96, 1) # 밝은 회색
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        # 화면 크기 변경 시 배경 크기 재조정 연결
        self.bind(size=self._update_rect, pos=self._update_rect)

        # 2. 메인 레이아웃 (기존 내용)
        root_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 상단 로고
        header = BoxLayout(size_hint_y=0.3)
        header.add_widget(Label(
            text="SH-TECH", 
            font_size='60sp', 
            color=(0.1, 0.4, 0.8, 1), 
            bold=True
        ))
        root_layout.add_widget(header)

        # 버튼 그리드
        grid = GridLayout(cols=2, spacing=20, padding=10)
        menu_items = [
            ("입고등록", "receiving"), ("입고반품", "return"),
            ("불출등록", "issue"), ("반입등록", "return_in"),
            ("외주입고", "out_rec"), ("외주출고", "out_iss")
        ]

        for text, screen_name in menu_items:
            btn = Button(
                text=text, font_size='22sp',
                background_normal='', 
                background_color=(0.1, 0.2, 0.35, 1)
            )
            btn.bind(on_press=lambda instance, s=screen_name: self.change_screen(s))
            grid.add_widget(btn)

        root_layout.add_widget(grid)
        root_layout.add_widget(BoxLayout(size_hint_y=0.2))
        
        self.add_widget(root_layout)

    # [중요] 이 함수는 __init__과 같은 라인(클래스 내부)에 있어야 합니다.
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def change_screen(self, screen_name):
        self.manager.transition.direction = 'left'
        self.manager.current = screen_name

# --- 메인 앱 클래스 ---
class PDAMainApp(MDApp):
    def build(self):
        # 1. 화면 관리자 생성
        sm = ScreenManager()
        
        # 2. 메인 메뉴 추가
        sm.add_widget(MainMenuScreen(name='main_menu'))
        
        # 3. 각 기능별 서브 화면 추가
        sm.add_widget(ReceivingScreen(name='receiving'))
        sm.add_widget(SubScreen(name='return', title_text="입고반품"))
        sm.add_widget(SubScreen(name='issue', title_text="불출등록"))
        sm.add_widget(SubScreen(name='return_in', title_text="반입등록"))
        sm.add_widget(SubScreen(name='out_rec', title_text="외주입고"))
        sm.add_widget(SubScreen(name='out_iss', title_text="외주출고"))
        
        return sm

if __name__ == '__main__':
    PDAMainApp().run()