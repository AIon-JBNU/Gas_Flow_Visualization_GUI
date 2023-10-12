from pygame.locals import *
from Gas_Flow_Visualization_GUI import *
import numpy as np
import os
import pygame
import PySimpleGUI as sg

class Sensor:  # 센서 8개 한번에 그리기
    def __init__(self, surface, x, y, cell_width, cell_height):
        self.surface = surface
        self.x = x
        self.y = y

        self.sensor_data = [[] for _ in range(8)]

        cell_x = x
        cell_y = y
        self.rect = []
        for i in range(8):
            self.rect.append(pygame.Rect(cell_x, cell_y, cell_width, cell_height))
            if i % 2 == 0:
                cell_x += cell_width
            else:
                cell_x = x
                cell_y += cell_height

    def change_sensor_data(self, index, data):
        self.sensor_data[index] = data

    def draw(self, time):
        changed = False
        for i in range(8):
            cur_data = self.sensor_data[i]
            time_data = cur_data[-1]
            if len(cur_data) > time:
                changed = True
                time_data = cur_data[time]
            data_first = cur_data[0]
            if data_first > time_data:  # 파랑색
                data_changed = data_first - time_data
                data_changed /= 700.0
                data_changed = min(1.0, data_changed)
                color = (0, int(255 * (1 - data_changed)), int(255 * data_changed))
            else:
                data_changed = time_data - data_first
                data_changed /= 700.0
                data_changed = min(1.0, data_changed)
                color = (int(255 * data_changed), int(255 * (1 - data_changed)), 0)
            pygame.draw.rect(self.surface, color, self.rect[i])

        return changed
def gas_flow_visualization_gui():
    layout = [
        [sg.Text("Gas Flow Visualization", size=(30, 1), justification="center", font=("Helvetica", 20))],
        [sg.Text("데이터가 위치한 폴더의 주소를 입력하세요")],
        [sg.InputText(key="folder_path"), sg.FolderBrowse()],
        [sg.Button("확인", size=(10, 1))]
    ]

    window = sg.Window("Gas Flow Visualization", layout, resizable=True)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "확인":
            folder_path = values["folder_path"]
            if not folder_path:
                sg.popup("폴더 경로를 입력하세요.")
            elif not os.path.exists(folder_path):
                sg.popup(f"경로가 존재하지 않습니다: {folder_path}")
            else:
                pygame_path(folder_path)
    window.close()

def pygame_path(folder_path):
    subdirectories = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

    layout = [
        [sg.Text("시각화할 가스 데이터가 있는 디렉토리를 선택해주세요")],
        [sg.Combo(subdirectories, key="selected_directory", size=(30, 1))],
        [sg.Text("Number:"), sg.Combo(list(range(1, 21)), key="selected_number", size=(5, 1))],
        [sg.Text("Heater:"), sg.Combo(['400V', '450V', '500V', '550V', '600V'], key="selected_heater", size=(5, 1))],
        [sg.Text("Fan:"), sg.Combo(['000', '060', '100'], key="selected_fan", size=(5, 1))],
        [sg.Button("확인", size=(10, 1))],
    ]

    window = sg.Window("디렉토리 선택", layout, resizable=True)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "확인":
            selected_directory = values["selected_directory"]
            selected_number = values["selected_number"]
            selected_heater = values["selected_heater"]
            selected_fan = values["selected_fan"]

            if not selected_directory:
                sg.popup("디렉토리를 선택하세요.")

            elif not selected_number:
                sg.popup("number를 선택하세요.")
            elif not selected_heater:
                sg.popup("heater를 선택하세요.")
            elif not selected_fan:
                sg.popup("fan를 선택하세요.")
            else:
                full_path = f"{folder_path}/{selected_directory}"
                print(full_path)
                data_extract(full_path, selected_number, selected_heater, selected_fan)
                break
    window.close()

def data_extract(full_path, selected_number, selected_heater, selected_fan):
    data_list = {}
    for i in range(1, 7):
        data_list[i] = {}
        for j in range(1, 21):
            data_list[i] = {}

    for i in range(1, 7):
        number = 0
        for file in os.listdir(f"{full_path}/L{str(i)}"):
            file_name_split = file.split("_")

            heater = file_name_split[3]
            fan = file_name_split[6]
            if heater == selected_heater and fan == selected_fan:
                number += 1
                if number == selected_number:
                    file_name = f"{full_path}/L{str(i)}/{file}"
                    data_list[i] = np.load(file_name)
                    print(file_name)
    gas_info = f"{os.path.basename(full_path)} number: {selected_number} heater: {selected_heater} fan: {selected_fan}"
    show_pygame(data_list, gas_info)


def show_pygame(data_list, gas_info):
    pygame.init()
    screen = pygame.display.set_mode((1200, 900))
    pygame.display.set_caption(gas_info)

    clock = pygame.time.Clock()
    running = True

    sensor_list = [] # 540 + 160 = 700
    sensor_x = 300
    sensor_y = 100
    sensor_width = 10
    sensor_height = 15
    for line in range(6): # L1 ~ L6
        sensor_list.append([])
        for i in range(9): # 가로로 센서 9개
            sensor = Sensor(screen, sensor_x, sensor_y, sensor_width, sensor_height)
            for j in range(8):
                sensor.change_sensor_data(j, data_list[line + 1][i, :, j])
            sensor_list[line].append(sensor)
            sensor_y += sensor_height * 4 + 20
        sensor_y = 100
        sensor_x += 150

    cur_time = 0
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        screen.fill("white")

        all_end = True

        for line in range(len(sensor_list)):
            for sensor_cnt in range(len(sensor_list[line])):
                sensor = sensor_list[line][sensor_cnt]
                changed = sensor.draw(cur_time)
                if changed:
                    all_end = False

        if all_end:
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(0, 0, 50, 50))

        cur_time += 1
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def main():
    gas_flow_visualization_gui()

if __name__=="__main__":
    main()
