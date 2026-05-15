from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# 한글 폰트 설정
KOREAN_FONT = "C:\\Windows\\Fonts\\malgun.ttf"
LabelBase.register(name="Roboto", fn_regular=KOREAN_FONT)

class MyPDAScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MyPDAScreen, self).__init__(**kwargs)
        # 레이아웃 설정 : 위에서 아래로 쌓기
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 10

        # 1. 제목 레이블
        self.add_widget(Label(
            text='PDA 재고 조회',
            font_size='24sp',
            size_hint_y=0.2,
            #font_name=KOREAN_FONT
        ))

        # 2. 바코드 입력창
        self.barcode_input = TextInput(
            hint_text='바코드를 스캔하거나 입력하세요',
            multiline=False,
            size_hint_y=0.2,
            #font_name=KOREAN_FONT
        )
        self.add_widget(self.barcode_input)

        # 3. 조회 버튼
        self.search_button = Button(
            text='데이터 조회',
            size_hint_y=0.3,
            background_color=(0, 0.7, 0.9, 1),
            #font_name=KOREAN_FONT
            )
        self.search_button.bind(on_press=self.on_click_button) 
        self.add_widget(self.search_button)

        # 4. 결과 레이블 (이게 있어야 화면에 글자가 바뀝니다)
        self.result_label = Label(
            text='결과가 여기에 표시됩니다.',
            size_hint_y=0.3,
            #font_name=KOREAN_FONT
            )
        self.add_widget(self.result_label)

    def on_click_button(self, instance):
        barcode = self.barcode_input.text

        if not barcode:
            self.result_label.text = "바코드를 입력해주세요."
            return

        try:

            conn = pymssql.connect(
                server='127.0.0.1',
                user='sa',
                password='',
                database='KJMEDITECH_DB_260509'
            )

            cursor = conn.cursor()

            sql_query = "SELECT ITEM_NAME, ITEM_CODE, ITEM_GHBN FROM BE_ITEM_INFO WHERE ITEM_CODE = %s"
            cursor.execute(sql_query, (barcode,))

            result = cursor.fetchone()

            if result:
                # 결과 반영
                self.result_label.text = f"조회 성공: {result[0]}"
            else:
                self.result_label.text = "등록되지 않은 바코드입니다."

            conn.close()

        except Exception as e:
            self.result_label.text = f"연결 실패: {e}"
        # 이제 result_label이 존재하므로 정상 작동합니다.
        #self.result_label.text = f"스캔된 바코드: {barcode}\n(이제 MSSQL에서 조회를 시작합니다.)"



class PDAApp(App):
    def build(self):
        return MyPDAScreen()

if __name__ == '__main__':
    PDAApp().run()