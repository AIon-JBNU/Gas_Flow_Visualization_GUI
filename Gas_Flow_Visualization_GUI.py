import pygame

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
