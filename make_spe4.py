import cv2 as cv
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import sys
import os
from PIL import Image

class SpecialEffect(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("사진 특수 효과")
        self.setGeometry(200, 200, 800, 400)

        # 버튼 및 위젯 설정
        pictureButton = QPushButton("사진 읽기", self)
        embossButton = QPushButton("엠보싱", self)
        cartoonButton = QPushButton("카툰", self)
        sketchButton = QPushButton("연필 스케치", self)
        oilButton = QPushButton("유화", self)
        blurButton = QPushButton("블러", self)
        saveButton = QPushButton("저장하기", self)
        quitButton = QPushButton("나가기", self)

        self.pickCombo = QComboBox(self)
        self.pickCombo.addItems(["엠보싱", "카툰", "연필 스케치(명암)", "연필 스케치(컬러)", "유화", "블러"])
        
        self.label = QLabel("환영합니다.", self)
        self.effect_img = None  # 적용된 효과 이미지를 저장하는 변수

        # 슬라이더 추가 (값 범위 1~20으로 축소)
        self.sigma_s_slider = QSlider(Qt.Orientation.Horizontal, self)  # 효과 강도를 조정하는 슬라이더
        self.sigma_s_slider.setRange(1, 20)  # 슬라이더 범위 변경
        self.sigma_s_slider.setValue(5)  # 초기값을 5로 설정
        self.sigma_s_slider.setGeometry(10, 100, 200, 30)
        self.sigma_s_slider.valueChanged.connect(self.update_slider)

        # 버튼 위치 설정
        pictureButton.setGeometry(10, 10, 100, 30)
        embossButton.setGeometry(110, 10, 100, 30)
        cartoonButton.setGeometry(210, 10, 100, 30)
        sketchButton.setGeometry(310, 10, 100, 30)
        oilButton.setGeometry(410, 10, 100, 30)
        blurButton.setGeometry(510, 10, 100, 30)
        saveButton.setGeometry(510, 40, 100, 30)
        self.pickCombo.setGeometry(620, 40, 160, 30)
        quitButton.setGeometry(620, 80, 100, 30)
        self.label.setGeometry(10, 40, 500, 170)

        # 버튼에 기능 연결
        pictureButton.clicked.connect(self.pictureOpenFunction)
        embossButton.clicked.connect(self.embossFunction)
        cartoonButton.clicked.connect(self.cartoonFunction)
        sketchButton.clicked.connect(self.sketchFunction)
        oilButton.clicked.connect(self.oilFunction)
        blurButton.clicked.connect(self.blurFunction)
        saveButton.clicked.connect(self.saveFunction)
        quitButton.clicked.connect(self.quitFunction)

        # 이미지를 위한 변수 초기화
        self.img = None  

    def resize_image(self, image, max_size=800):
        height, width = image.shape[:2]
        if max(height, width) > max_size:
            scale_factor = max_size / float(max(height, width))
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = cv.resize(image, (new_width, new_height))
        return image

    def pictureOpenFunction(self):
        fname = QFileDialog.getOpenFileName(self, "사진읽기", "./")
        
        # 선택한 파일 경로 절대 경로로 변환
        file_path = fname[0]
        if not file_path:
            self.label.setText("파일을 선택하지 않았습니다.")
            return

        # 경로를 절대 경로로 변환하고, 경로가 유효한지 확인
        file_path = os.path.abspath(file_path)
        print(f"선택한 파일 경로: {file_path}")  # 디버깅용 출력
        
        # 이미지 파일 읽기
        self.img = cv.imread(file_path)
        if self.img is None: 
            self.label.setText(f"파일을 찾을 수 없습니다: {file_path}")
            return
        
        self.img = self.resize_image(self.img)
        cv.imshow("Painting", self.img)

    def update_slider(self):
        # 슬라이더 값이 변경될 때마다 레이블 업데이트
        self.label.setText(f"슬라이더 값: {self.sigma_s_slider.value()}")

    def embossFunction(self):
        if self.img is None: 
            self.label.setText("먼저 사진을 읽어오세요.")
            return
        femboss = np.array([[-1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        gray16 = np.int16(gray)
        self.effect_img = np.uint8(np.clip(cv.filter2D(gray16, -1, femboss) + 128, 0, 255))
        cv.imshow("Emboss", self.effect_img)

    def cartoonFunction(self):
        if self.img is None: 
            self.label.setText("먼저 사진을 읽어오세요.")
            return
        sigma_s = self.sigma_s_slider.value()  # 슬라이더 값 사용
        self.effect_img = cv.stylization(self.img, sigma_s=sigma_s, sigma_r=0.45)
        cv.imshow("Cartoon", self.effect_img)

    def sketchFunction(self):
        if self.img is None: 
            self.label.setText("먼저 사진을 읽어오세요.")
            return

        # 명암 및 컬러 스케치 두 가지 모두 생성 및 표시
        sigma_s = self.sigma_s_slider.value()  # 슬라이더 값 사용
        self.sketch_gray, self.sketch_color = cv.pencilSketch(self.img, sigma_s=sigma_s, sigma_r=0.07, shade_factor=0.02)

        # 두 스케치를 각각의 창에 표시
        cv.imshow("Pencil Sketch (Gray)", self.sketch_gray)
        cv.imshow("Pencil Sketch (Color)", self.sketch_color)

    def oilFunction(self):
        if self.img is None: 
            self.label.setText("먼저 사진을 읽어오세요.")
            return
        
        # 슬라이더 값을 사용하여 유화 효과의 강도 조절
        radius = self.sigma_s_slider.value()  # 슬라이더 값으로 radius 설정
        dynRatio = max(1, int(radius * 0.1))  # dynRatio는 1 이상이어야 함

        # 유화 효과 적용
        self.effect_img = cv.xphoto.oilPainting(self.img, radius, dynRatio, cv.COLOR_BGR2Lab)
        cv.imshow("Oil Painting", self.effect_img)

    def blurFunction(self):
        if self.img is None: 
            self.label.setText("먼저 사진을 읽어오세요.")
            return
        # 블러 강도 조절
        blur_strength = self.sigma_s_slider.value()
        self.effect_img = cv.GaussianBlur(self.img, (blur_strength | 1, blur_strength | 1), 0)  # 커널 사이즈는 홀수로 설정
        cv.imshow("Blurred Image", self.effect_img)

    def saveFunction(self):
        if self.effect_img is None:
            self.label.setText("먼저 효과를 적용하세요.")
            return

        # 선택된 특수 효과가 무엇인지 가져오기
        effect = self.pickCombo.currentText()

        # BGR -> RGB 변환 후 PIL로 저장
        img_rgb = cv.cvtColor(self.effect_img, cv.COLOR_BGR2RGB)
        img = Image.fromarray(img_rgb)

        fname, _ = QFileDialog.getSaveFileName(self, "파일 저장", "./", "Images (*.jpg *.png *.bmp)")
        if fname:
            if not (fname.endswith('.jpg') or fname.endswith('.png') or fname.endswith('.bmp')):
                fname += '.jpg'
            img.save(fname)
            self.label.setText(f"파일이 {fname}에 저장되었습니다.")

    def quitFunction(self):
        cv.destroyAllWindows()
        self.close()

app = QApplication(sys.argv)
win = SpecialEffect()
win.show()
sys.exit(app.exec())
