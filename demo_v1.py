import math
import threading
import pygame
from Demo.data import *
from sys import exit
import random
import subprocess
from threading import Thread
from ast import literal_eval
import socket
from os import chdir

import settings

# chdir('../')

pygame.init()
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
shares = None
max_shares = None
fps_lock = threading.Lock()
fps = 60
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
clock = pygame.time.Clock()

aspect_ratio_16x9 = True
screen_scalar_x = 1
screen_scalar_y = 1

if screen_width >= 1920 and screen_height >= 1080:
    map_blur_surf = pygame.image.load('./Demo/Graphics/DemoMapBlur1920x1080.png')
    map_surf = pygame.image.load('./Demo/Graphics/DemoMap1920x1080.png')
    screen_scalar_x = 1920 / 1600
    screen_scalar_y = 1080 / 900
elif screen_width >= 1440 and screen_height >= 1080:
    map_blur_surf = pygame.image.load('./Demo/Graphics/DemoMapBlur1440x1080.png')
    map_surf = pygame.image.load('./Demo/Graphics/DemoMap1440x1080.png')
    screen_scalar_x = 1440 / 1600
    screen_scalar_y = 1080 / 900
    aspect_ratio_16x9 = False
elif screen_width >= 1600 and screen_height >= 900:
    map_blur_surf = pygame.image.load('./Demo/Graphics/DemoMapBlur1600x900.png')
    map_surf = pygame.image.load('./Demo/Graphics/DemoMap1600x900.png')
elif screen_width >= 1024 and screen_height >= 768:
    map_blur_surf = pygame.image.load('./Demo/Graphics/DemoMapBlur1024x768.png')
    map_surf = pygame.image.load('./Demo/Graphics/DemoMap1024x768.png')
    screen_scalar_x = 1024 / 1600
    screen_scalar_y = 768 / 900
    aspect_ratio_16x9 = False
else:
    map_blur_surf = pygame.image.load('./Demo/Graphics/DemoMapBlur1024x576.png')
    map_surf = pygame.image.load('./Demo/Graphics/DemoMap1024x576.png')
    screen_scalar_x = 1024 / 1600
    screen_scalar_y = 576 / 900
    screen_width = 1024
    screen_height = 576

pygame.display.set_caption('Radarsignature Demo')

stencil_font = pygame.font.Font('./Demo/Fonts/QTMilitary.otf', int(15 * screen_scalar_x))
coprgtb_font = pygame.font.Font('./Demo/Fonts/CopperplateCC-Bold.otf', int(10 * screen_scalar_y))

black = (0, 0, 0, 0)
red = (150, 0, 0, 0)
yellow = (150, 150, 0, 0)
green = (0, 150, 0, 0)
white = (255, 255, 255, 0)
dark_green = [0, 228, 0, 128]

fifty_km_in_pix = 250 * screen_scalar_x

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, button_text, id=-1):
        super().__init__()
        self.id = id
        self.x = x
        self.y = y
        self.shadow_x = x + 5 * screen_scalar_x
        self.shadow_y = y + 5 * screen_scalar_y
        self.width = width
        self.height = height
        self.name = button_text
        self.fill_colors = {
            'normal': (255, 255, 255),  # White
            'pressed': (128, 128, 128), # Grey
            'blocked': (164, 90, 82),  # Redwood
        }
        self.button_surface = pygame.Surface((self.width, self.height))
        self.button_surface.set_alpha(192)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.image = stencil_font.render(self.name, True, (20, 20, 20))
        self.button_surface.fill(self.fill_colors['normal'])
        self.shadow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.shadow_surf.fill((0, 0, 0, 128))
        self.pressed = False
        self.blocked = False

    def set_unblocked(self):
        self.button_surface.fill(self.fill_colors['normal'])
        self.blocked = False

    def set_blocked(self):
        self.button_surface.fill(self.fill_colors['blocked'])
        self.blocked = True

    def is_clicked(self):
        if not self.pressed:
            self.button_surface.fill(self.fill_colors['pressed'])
            self.pressed = True
            self.rect.x += 5 * screen_scalar_x
            self.rect.y += 5 * screen_scalar_y
        else:
            self.button_surface.fill(self.fill_colors['normal'])
            self.pressed = False
            self.rect.x -= 5 * screen_scalar_x
            self.rect.y -= 5 * screen_scalar_y

    def draw(self):
        screen.blit(self.shadow_surf, (self.shadow_x, self.shadow_y))
        self.button_surface.blit(self.image, [
            self.rect.width / 2 - self.image.get_rect().width / 2,
            self.rect.height / 2 - self.image.get_rect().height / 2
        ])
        screen.blit(self.button_surface, self.rect)

    def update(self):
        self.draw()


class Dot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, color, dir_x, dir_y, speed, delay, port, host):
        super().__init__()
        self.init_delay = delay
        self.timer = 0

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed_x = self.dir_x * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * 1500
        self.speed_y = self.dir_y * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * 1500
        self.speed_multiple = speed   # speed_multiple * 25kph = real speed
        self.name = ''
        self.name_rect = None
        self.color = color
        self.image = stencil_font.render('•', True, self.color)
        self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))
        self.radar = Radar()
        self.pulse_sent = False
        self.detected = False
        self.searching = False
        self.identified = False
        self.kill_delay = 60 * 60 * 5  # 5 minutes

        self.protocol = None
        self.protocol_output = None

        self.real_speed = False

        self.port = port
        self.host = '.'.join(map(str, host))

    def set_pause(self):
        self.speed_x = 0
        self.speed_y = 0

    def set_unpause(self):
        if not self.detected:
            self.speed_x = self.dir_x * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * 500
            self.speed_y = self.dir_y * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * 500
        else:
            self.speed_x = self.dir_x * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * self.speed_multiple
            self.speed_y = self.dir_y * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * self.speed_multiple

    def draw(self):
        if self.detected:
            name_surf = stencil_font.render(self.name, True, self.color)
            self.name_rect = name_surf.get_rect(midbottom=self.rect.midtop)
            screen.blit(name_surf, self.name_rect)

    def move(self):
        self.pos_x += self.speed_x * (60 / fps)
        self.pos_y += self.speed_y * (60 / fps)
        self.rect.center = (self.pos_x, self.pos_y)

    def radar_scan(self):
        self.radar.speed_update()
        if not self.pulse_sent:
            self.pulse_sent = self.radar.send_pulse(self.rect.centerx, self.rect.centery)
        else:
            self.pulse_sent = self.radar.update_pulse()

    def check_detected(self):
        if not self.detected:
            if self.radar.check_detected():
                self.detected = True
                self.color = yellow
                self.name = 'unknown'

    def check_identified(self):
        global active_dots

        if not self.searching:
            self.protocol = Protocol(self.port, self.host)
            self.protocol.start()
            self.searching = True
        elif not self.protocol.is_alive():
            self.protocol.join()
            if self.protocol.output is not None:
                self.protocol_output = literal_eval(self.protocol.output)
                self.identified = self.protocol.finished
                print(self.protocol_output)
                radar_signature = sorted((x for x in self.protocol_output if (x[1] > 0)), key=lambda x: x[1])
                if len(radar_signature) > 0:
                    radar_signature = radar_signature[0][0]
                    self.name = vessel_id_to_name[radar_signature][0]
                    if vessel_id_to_name[radar_signature][2]:
                        self.color = red
                    else:
                        self.color = green
                else:
                    self.color = red
                    self.name = 'Unidentified'
            self.identified = True
            active_dots -= 1

    def check_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(mouse_pos) or self.name_rect.collidepoint(mouse_pos):
                print("info box")

    def update(self):
        if self.timer < self.init_delay:
            self.timer += 1
            return

        #if self.detected:
        #  self.check_clicked()

        self.move()

        if not self.detected:
            if not self.real_speed:
                if antenna.in_antenna_range(self.pos_x, self.pos_y):
                    self.speed_x = self.dir_x * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * self.speed_multiple
                    self.speed_y = self.dir_y * (fifty_km_in_pix / (2 * 60 * 60 * 60)) * self.speed_multiple
                    self.real_speed = True

            self.radar_scan()
            self.check_detected()

        if self.detected and not self.identified:
            self.check_identified()

        if self.identified:
            if self.kill_delay <= 0:
                self.kill()
            self.kill_delay -= 1 * (60 / fps)

        if self.check_outside_map():
            self.kill()
            global active_dots
            active_dots -= 1

        self.draw()

    def check_outside_map(self):
        if self.rect.centerx < 0 or self.rect.centery < 0 or screen_width < self.rect.centerx or screen_height < self.rect.centery:
            return True

        return False


class Antenna:
    def __init__(self):
        if aspect_ratio_16x9:
            self.strength = 608 * screen_scalar_x
            self.pos_x = 881 * screen_scalar_x
            self.pos_y = 730 * screen_scalar_y
        else:
            self.strength = 800 * screen_scalar_x
            self.pos_x = 830 * screen_scalar_x
            self.pos_y = 710 * screen_scalar_y

    def in_antenna_range(self, pos_x, pos_y):
        distance = math.sqrt((pos_x - self.pos_x) ** 2 + (pos_y - self.pos_y) ** 2)
        if distance <= self.strength:
            return True

        return False


class Radar:
    def __init__(self):
        self.pos_x = None
        self.pos_y = None
        self.sent = False
        self.radius = 0
        self.decay = None
        self.speed = None
        self.color = [0, 228, 0, 255]  # Dark Green with 50% transparency

    def send_pulse(self, pos_x, pos_y):
        self.radius = 0
        self.color[3] = 255
        self.pos_x = pos_x
        self.pos_y = pos_y
        return True

    def update_pulse(self):
        self.radius += self.speed

        if not self.color[3] < self.decay:  # Decays pulse
            self.color[3] -= self.decay

        surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        pygame.draw.circle(surface=surface, color=self.color, center=(self.pos_x, self.pos_y),
                           radius=self.radius, width=int(2 * screen_scalar_x))
        screen.blit(surface, (0, 0))

        if antenna.strength < self.radius:
            return False

        return True

    def speed_update(self):
        global fps

        self.decay = 2 * (60 / fps) * screen_scalar_x
        self.speed = 5 * (60 / fps) * screen_scalar_x

    def check_detected(self):
        distance = math.sqrt((self.pos_x - antenna.pos_x) ** 2 + (self.pos_y - antenna.pos_y) ** 2)
        if (distance - self.radius) <= 0:
            return True

        return False


class Protocol(Thread):
    def __init__(self, port, host):
        Thread.__init__(self)
        self.output = None
        self.error = None
        self.finished = False
        self.port = port
        self.host = host

    def run(self):
        global number_of_databases, is_multiplayer

        self.cap_fps()

        if not is_multiplayer:
            self.run_mpc_protocol_single_pc()
        else:
            self.run_mpc_protocol()

        self.free_fps()

        self.finished = True

    def cap_fps(self):
        global shares, fps, fps_lock

        fps_lock.acquire(blocking=True)

        if shares == max_shares:
            fps = 15
        shares -= 1

        fps_lock.release()

    def free_fps(self):
        global shares, fps, fps_lock

        fps_lock.acquire(blocking=True)

        shares += 1
        if shares == max_shares:
            fps = 60

        fps_lock.release()

    def run_mpc_protocol_single_pc(self):
        global number_of_databases

        match number_of_databases:
            case 1:
                process_measurement = subprocess.Popen([settings.protocol_path, '-p', '0', '-IF', settings.measurement_input, '-pn',
                                                        f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                        'classifier_single_db_ors', '-t'] + settings.protocol_options, stdout=subprocess.PIPE, text=True)
                process_database = subprocess.Popen([settings.protocol_path,  '-p', '1', '-IF', settings.database_input_single, '-pn',
                                                     f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                     'classifier_single_db_ors', '-t'],  stdout=subprocess.PIPE, text=True)
                self.output, self.error = process_measurement.communicate()
                process_measurement.kill()
                process_database.kill()
            case 2:
                process_measurement = subprocess.Popen([settings.protocol_path, '-p', '0', '-IF', settings.measurement_input, '-pn',
                                                        f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                        'classifier_double_db_ors', '-t'] + settings.protocol_options, stdout=subprocess.PIPE,
                                                       text=True)
                process_database_1 = subprocess.Popen([settings.protocol_path, '-p', '1', '-IF', settings.database_input_double, '-pn',
                                                       f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                       'classifier_double_db_ors', '-t'] + settings.protocol_options,  stdout=subprocess.PIPE,
                                                      text=True)
                process_database_2 = subprocess.Popen([settings.protocol_path, '-p', '2', '-IF', settings.database_input_double, '-pn',
                                                       f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                       'classifier_double_db_ors', '-t'] + settings.protocol_options,  stdout=subprocess.PIPE,
                                                      text=True)
                self.output, self.error = process_measurement.communicate()
                process_measurement.kill()
                process_database_1.kill()
                process_database_2.kill()
            case 3:
                process_measurement = subprocess.Popen([settings.protocol_path, '-p', '0', '-IF', settings.measurement_input, '-pn',
                                                        f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                        'classifier_triple_db_ors', '-t'] + settings.protocol_options, stdout=subprocess.PIPE,
                                                       text=True)
                process_database_1 = subprocess.Popen([settings.protocol_path, '-p', '1', '-IF', settings.database_input_triple, '-pn',
                                                       f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                       'classifier_triple_db_ors', '-t'] + settings.protocol_options,  stdout=subprocess.PIPE,
                                                      text=True)
                process_database_2 = subprocess.Popen([settings.protocol_path, '-p', '2', '-IF', settings.database_input_triple, '-pn',
                                                       f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                       'classifier_triple_db_ors', '-t'] + settings.protocol_options, stdout=subprocess.PIPE,
                                                      text=True)
                process_database_3 = subprocess.Popen([settings.protocol_path, '-p', '3', '-IF', settings.database_input_triple, '-pn',
                                                       f'{self.port}', '-N', f'{number_of_databases + 1}',
                                                       'classifier_triple_db_ors', '-t'] + settings.protocol_options,  stdout=subprocess.PIPE,
                                                      text=True)
                self.output, self.error = process_measurement.communicate()
                process_measurement.kill()
                process_database_1.kill()
                process_database_2.kill()
                process_database_3.kill()

    def run_mpc_protocol(self):
        global number_of_databases, player_id

        match number_of_databases:
            case 1:
                process_measurement = subprocess.Popen([settings.protocol_path, '-p', '0', '-IF', settings.measurement_input, '-pn',
                                                        '-h', f'{self.host}', f'{self.port}', '-N',
                                                        f'{number_of_databases + 1}', 'classifier_single_db_ors', '-t'] + settings.protocol_options,
                                                       stdout=subprocess.PIPE, text=True)
                process_database = subprocess.Popen([settings.protocol_path, '-p', '1', '-IF', settings.database_input_single, '-pn',
                                                     '-h', f'{self.host}', f'{self.port}', '-N',
                                                     f'{number_of_databases + 1}', 'classifier_single_db_ors', '-t'] + settings.protocol_options,
                                                    stdout=subprocess.PIPE, text=True)
                self.output, self.error = process_measurement.communicate()
                process_measurement.kill()
                process_database.kill()
            case 2:
                if player_id == 1:
                    process_measurement = subprocess.Popen([settings.protocol_path, '-p', '0', '-IF', settings.measurement_input,
                                                            '-h', f'{self.host}', '-pn', f'{self.port}', '-N',
                                                            f'{number_of_databases + 1}',
                                                            'classifier_double_db_ors', '-t'] + settings.protocol_options,
                                                           stdout=subprocess.PIPE, text=True)
                    process_database_1 = subprocess.Popen([settings.protocol_path, '-p', '1', '-IF', settings.database_input_double,
                                                           '-h', f'{self.host}', '-pn', f'{self.port}', '-N',
                                                           f'{number_of_databases + 1}',
                                                           'classifier_double_db_ors', '-t'] + settings.protocol_options,
                                                          stdout=subprocess.PIPE, text=True)
                    self.output, self.error = process_measurement.communicate()
                    process_measurement.kill()
                    process_database_1.kill()

                else:
                    process_database_2 = subprocess.Popen([settings.protocol_path, '-p', '2', '-IF', settings.database_input_double,
                                                           '-h', f'{self.host}', '-pn', f'{self.port}', '-N',
                                                           f'{number_of_databases + 1}', 'classifier_double_db_ors',
                                                           '-t'] + settings.protocol_options, stdout=subprocess.PIPE, text=True)
                    process_database_2.wait()
                    process_database_2.kill()
            case 3:
                if player_id == 1:
                    process_measurement = subprocess.Popen([settings.protocol_path, '-p', '0', '-IF', settings.measurement_input,
                                                            '-h', f'{self.host}', '-pn', f'{self.port}', '-N',
                                                            f'{number_of_databases + 1}', 'classifier_triple_db_ors',
                                                            '-t'] + settings.protocol_options, stdout=subprocess.PIPE, text=True)
                    process_database_1 = subprocess.Popen([settings.protocol_path, '-p', '1', '-IF', settings.database_input_triple,
                                                           '-h', f'{self.host}', '-pn', f'{self.port}', '-N',
                                                           f'{number_of_databases + 1}', 'classifier_triple_db_ors',
                                                           '-t'] + settings.protocol_options,  stdout=subprocess.PIPE, text=True)
                    self.output, self.error = process_measurement.communicate()
                    process_measurement.kill()
                    process_database_1.kill()
                elif player_id == 2:
                    process_database_2 = subprocess.Popen([settings.protocol_path, '-p', '2', '-IF', settings.database_input_triple,
                                                           '-h', f'{self.host}', '-pn', f'{self.port}', '-N',
                                                           f'{number_of_databases + 1}', 'classifier_triple_db_ors',
                                                           '-t'] + settings.protocol_options, stdout=subprocess.PIPE, text=True)
                    process_database_2.wait()
                    process_database_2.kill()
                else:
                    process_database_3 = subprocess.Popen([settings.protocol_path, '-p', '3', '-IF', settings.database_input_triple,
                                                           '-h', f'{self.host}', '-pn', f'{self.port}', '-N',
                                                           f'{number_of_databases + 1}', 'classifier_triple_db_ors',
                                                           '-t'] + settings.protocol_options,  stdout=subprocess.PIPE, text=True)
                    process_database_3.wait()
                    process_database_3.kill()


class Communicate:
    def __init__(self, ip, port):
        self.HEADER = 128
        self.LISTEN_PORT = port
        self.HOST = ip
        self.CLIENTS_ON_NETWORK = [('10.0.0.10', 9000), ('10.0.0.11', 9001), ('10.0.0.12', 9002), ('10.0.0.13', 9003)]
        self.ADDR = (self.HOST, self.LISTEN_PORT)
        self.FORMAT = 'utf-8'
        self.UNREADY_MESSAGE = 'UNREADY'
        self.READY_MESSAGE = 'READY'
        self.SYNC_MESSAGE = 'SYNC'
        self.DISCONNECT_MESSAGE = 'CLOSE'
        self.listen_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_host.settimeout(0.2)
        self.close = False
        self.listen_thread = []
        self.run_thread = threading.Thread(target=self.run)
        self.run_thread.start()
        self.on_network = set()
        self.num_ready = 0

    def add_padding(self, msg):
        message = msg.encode(self.FORMAT)
        message += b' ' * (self.HEADER - len(message))
        return message

    def send_unready(self):
        send_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for addr in self.on_network:
            send_host.connect(addr)
            send_host.send(self.add_padding(self.UNREADY_MESSAGE))
            send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
            send_host.close()

        self.num_ready -= 1
        print(f'[SENT] {self.UNREADY_MESSAGE} to {self.on_network}')

    def send_ready(self):
        send_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for addr in self.on_network:
            send_host.connect(addr)
            send_host.send(self.add_padding(self.READY_MESSAGE))
            send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
            send_host.close()

        self.num_ready += 1
        print(f'[SENT] {self.READY_MESSAGE} to {self.on_network}')

    def rendezvous(self):
        send_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for addr in self.CLIENTS_ON_NETWORK:
            if addr[0] != self.HOST:
                try:
                    send_host.connect(addr)
                    send_host.send(self.add_padding(self.SYNC_MESSAGE))
                    send_host.send(self.add_padding(f'("{self.HOST}", {self.LISTEN_PORT})'))
                    send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
                    send_host.close()

                    self.on_network.add(addr)
                except OSError as e:
                    pass

        print(f'[CLIENT DISCOVERED] CLIENTS ON NETWORK: {self.on_network}')

    def receive(self, conn, addr):
        while True:
            msg = conn.recv(self.HEADER).decode(self.FORMAT).strip()
            print(f'[RECEIVED] {msg} from {addr}')
            if msg == self.DISCONNECT_MESSAGE:
                return
            elif msg == self.SYNC_MESSAGE:
                message = conn.recv(self.HEADER).decode(self.FORMAT)
                self.on_network.add(literal_eval(message))
                print(f'[CLIENT DISCOVERED] CLIENTS ON NETWORK: {self.on_network}')
            elif msg == self.READY_MESSAGE:
                self.num_ready += 1
            elif msg == self.UNREADY_MESSAGE:
                self.num_ready -= 1
            else:
                dots.add(Dot(*literal_eval(msg)))

    def send_dot(self, dot_values):
        send_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for addr in self.on_network:
            send_host.connect(addr)
            send_host.send(self.add_padding(f'{dot_values}'))
            send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
            send_host.close()

    def run(self):
        self.listen_host.bind(self.ADDR)
        self.listen_host.listen()
        print(f'[{self.HOST} LISTENING ON {self.LISTEN_PORT}]')
        while True:
            if self.close:
                return

            try:
                conn, addr = self.listen_host.accept()
                thread = threading.Thread(target=self.receive, args=(conn,addr))
                thread.start()
                self.listen_thread.append(thread)
            except socket.timeout:
                pass
            except OSError:
                pass

    def kill(self):
        for thread in self.listen_thread:
            thread.join()
        self.listen_host.close()
        self.close = True
        self.run_thread.join()

    def all_ready(self):
        if self.num_ready == len(self.on_network) + 1 and len(self.on_network) > 0:
            return True

        return False

    def all_ready_except_self(self):
        if self.num_ready == len(self.on_network) and len(self.on_network) > 0:
            return True

        return False


def stage1():
    global buttons

    if aspect_ratio_16x9:
        single_button_x = (screen_width / 3) - screen_width * 0.125
        single_button_y = (screen_height / 2) - screen_height * 0.0556
        single_button_width = screen_width * 0.25
        single_button_height =screen_height * 0.1112
        multi_button_x = (screen_width / 3) * 2 - screen_width * 0.125
        multi_button_y = (screen_height / 2) - screen_height * 0.0556
        multi_button_width = screen_width * 0.25
        multi_button_height = screen_height * 0.1112
    else:
        single_button_x = (screen_width / 3) - screen_width * 0.125
        single_button_y = (screen_height / 2) - screen_height * 0.0556
        single_button_width = screen_width * 0.25
        single_button_height =screen_height * 0.1112
        multi_button_x = (screen_width / 3) * 2 - screen_width * 0.125
        multi_button_y = (screen_height / 2) - screen_height * 0.0556
        multi_button_width = screen_width * 0.25
        multi_button_height = screen_height * 0.1112


    buttons.add(Button(single_button_x, single_button_y, single_button_width, single_button_height, 'Single PC'))
    buttons.add(Button(multi_button_x, multi_button_y, multi_button_width, multi_button_height, 'Multi PC'))


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in buttons:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            button.is_clicked()
                            if button.pressed and button.name == 'Single PC':
                                return 0
                            elif button.pressed and button.name == 'Multi PC':
                                return 1

        screen.blit(map_blur_surf, (0, 0))
        buttons.update()
        pygame.display.update()
        clock.tick(fps)


def stage2():
    global buttons

    buttons.empty()
    buttons.add(Button(screen_width * 0.0188, screen_height * 0.0334, screen_width * 0.0313, screen_height * 0.0278, 'Back'))
    buttons.add(Button(30 * screen_scalar_x, 600 * screen_scalar_y, 400 * screen_scalar_x, 100 * screen_scalar_y, 'Single Database'))
    buttons.add(Button(screen_width / 2 - (200 * screen_scalar_x) - (15 * screen_scalar_x), 600 * screen_scalar_y, 400 * screen_scalar_x, 100 * screen_scalar_y, 'Double Database'))
    buttons.add(Button(screen_width - (400 * screen_scalar_x) - (30 * screen_scalar_x), 600 * screen_scalar_y, 400 * screen_scalar_x, 100 * screen_scalar_y, 'Triple Database'))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in buttons:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            button.is_clicked()
                            if button.pressed and button.name == 'Back':
                                return -1
                            elif button.pressed and button.name == 'Single Database':
                                return 1
                            elif button.pressed and button.name == 'Double Database':
                                return 2
                            elif button.pressed and button.name == 'Triple Database':
                                return 3

        screen.blit(map_blur_surf, (0, 0))
        buttons.update()
        pygame.display.update()
        clock.tick(fps)


def stage3():
    global communicator, player_id, buttons, is_multiplayer, ip, port

    screen.blit(map_blur_surf, (0, 0))

    buttons.update()
    pygame.display.update()
    clock.tick(fps)

    communicator = Communicate(ip, port)
    communicator.rendezvous()

    buttons.empty()
    buttons.add(Button(screen_width * 0.0188, screen_height * 0.0334, screen_width * 0.0313, screen_height * 0.0278, 'Back'))
    buttons.add(Button(screen_width * 0.0188, screen_height * 0.6667, screen_width * 0.25, screen_height * 0.1112, 'Player 1'))
    buttons.add(Button(screen_width / 2 - screen_width * 0.1354, screen_height * 0.6667, screen_width * 0.25, screen_height * 0.1112, 'Player 2'))
    buttons.add(Button(screen_width - screen_width * 0.2688, screen_height * 0.6667, screen_width * 0.25, screen_height * 0.1112, 'Player 3'))
    buttons.add(Button(screen_width / 2 - screen_width * 0.1969, screen_height * 0.2223, screen_width * 0.375, screen_height * 0.1112, 'Start'))

    for button in buttons:
        if button.name == 'Start' and len(communicator.on_network) < 1:
            button.set_blocked()
        if button.name == 'Player 2' and len(communicator.on_network) < 1:
            button.set_blocked()
        if button.name == 'Player 3' and len(communicator.on_network) < 2:
            button.set_blocked()

    player_id = -1

    timer = 0

    while True:
        for button in buttons:
            if button.blocked:
                if button.name == 'Player 2' and len(communicator.on_network) >= 1:
                    button.set_unblocked()
                if button.name == 'Player 3' and len(communicator.on_network) >= 2:
                    button.set_unblocked()
                if button.name == 'Start' and len(communicator.on_network) >= 1:
                    button.set_unblocked()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                if is_multiplayer:
                    communicator.kill()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in buttons:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            if button.name == 'Back':
                                communicator.kill()
                                return -1, -1
                            if timer == 0:
                                timer = 30
                                if button.name == 'Player 1' and not button.blocked:
                                    button.is_clicked()
                                    if button.pressed:
                                        player_id = 1
                                        for b in buttons:
                                            if b.pressed and not b.name == 'Player 1':
                                                b.is_clicked()
                                                if b.name == 'Start':
                                                    communicator.send_unready()
                                    else:
                                        for b in buttons:
                                            if b.name == 'Start' and b.pressed:
                                                b.is_clicked()
                                                communicator.send_unready()
                                        player_id = -1
                                elif button.name == 'Player 2' and not button.blocked:
                                    button.is_clicked()
                                    if button.pressed:
                                        player_id = 2
                                        for b in buttons:
                                            if b.pressed and not b.name == 'Player 2':
                                                b.is_clicked()
                                                if b.name == 'Start':
                                                    communicator.send_unready()
                                    else:
                                        for b in buttons:
                                            if b.name == 'Start' and b.pressed:
                                                b.is_clicked()
                                                communicator.send_unready()
                                        player_id = -1
                                elif button.name == 'Player 3' and not button.blocked:
                                    button.is_clicked()
                                    if button.pressed:
                                        player_id = 3
                                        for b in buttons:
                                            if b.pressed and not b.name == 'Player 3':
                                                b.is_clicked()
                                                if b.name == 'Start':
                                                    communicator.send_unready()
                                    else:
                                        for b in buttons:
                                            if b.name == 'Start' and b.pressed:
                                                b.is_clicked()
                                                communicator.send_unready()
                                        player_id = -1
                                elif button.name == 'Start' and not button.blocked:
                                    button.is_clicked()
                                    if button.pressed:
                                        if player_id == 1:
                                            if communicator.all_ready_except_self():
                                                communicator.send_ready()
                                            else:
                                                button.is_clicked()
                                        elif player_id != -1:
                                            communicator.send_ready()
                                        else:
                                            button.is_clicked()
                                            print('Choose Player ID')
                                    else:
                                        communicator.send_unready()

        if communicator.all_ready():
            return communicator.num_ready, player_id

        if timer != 0:
            timer -= 1

        screen.blit(map_blur_surf, (0, 0))

        buttons.update()
        pygame.display.update()
        clock.tick(fps)


def get_vessel_buttons(vessel_ids):
    global buttons

    counter_columns = 0
    counter_rows = 0
    num_columns = 12
    # num_rows = 9
    init_height = screen_height / 3
    box_width = screen_width * 0.0781
    box_height = screen_height * 0.0556
    space_width = screen_width * 0.0025
    space_height = screen_height * 0.0167

    for vessel_id in vessel_ids:
        if counter_columns == 0:
            counter_rows = (counter_rows + 1)

        buttons.add(Button(space_width + space_width * counter_columns + box_width * counter_columns,
                           init_height + space_height + space_height * counter_rows + box_height * counter_rows,
                           box_width, box_height, vessel_id_to_name[vessel_id][0], vessel_id))

        counter_columns = (counter_columns + 1) % num_columns


def stage4():
    global is_multiplayer, player_id, number_of_databases, vessel_id

    if is_multiplayer:
        communicator.num_ready = 0

    dots.empty()

    buttons.empty()
    buttons.add(Button(screen_width * 0.0188, screen_height * 0.0334, screen_width * 0.0313, screen_height * 0.0278, 'Back'))
    buttons.add(Button(screen_width / 2 - screen_width * 0.1969, screen_height * 0.2223, screen_width * 0.375, screen_height * 0.1112, 'Start'))

    vessel_id = -1

    timer = 0
    if is_multiplayer:
        match number_of_databases:
            case 1:
                get_vessel_buttons(database_P1_single)
            case 2:
                if player_id == 1:
                    get_vessel_buttons(database_P1_double)
                else:
                    get_vessel_buttons(database_P2_double)
            case 3:
                if player_id == 1:
                    get_vessel_buttons(database_P1_triple)
                elif player_id == 2:
                    get_vessel_buttons(database_P2_triple)
                else:
                    get_vessel_buttons(database_P3_triple)
    else:
        get_vessel_buttons(database_P1_single)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                if is_multiplayer:
                    communicator.kill()
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in buttons:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            if button.name == 'Back':
                                if is_multiplayer:
                                    communicator.kill()
                                return -1
                            if timer == 0:
                                timer = 30
                                if button.name != 'Start':
                                    button.is_clicked()
                                    if button.pressed:
                                        for b in buttons:
                                            if b.pressed and not b.name == button.name:
                                                b.is_clicked()
                                                if b.name == 'Start' and is_multiplayer:
                                                    communicator.send_unready()
                                        vessel_id = button.id
                                    else:
                                        for b in buttons:
                                            if b.name == 'Start' and b.pressed:
                                                b.is_clicked()
                                                if is_multiplayer:
                                                    communicator.send_unready()
                                        vessel_id = -1
                                elif button.name == 'Start':
                                    button.is_clicked()
                                    if is_multiplayer:
                                        if button.pressed:
                                            if player_id == 1 and vessel_id != -1:
                                                if communicator.all_ready_except_self():
                                                    communicator.send_ready()
                                                else:
                                                    button.is_clicked()
                                            elif player_id != -1 and vessel_id != -1:
                                                communicator.send_ready()
                                            else:
                                                button.is_clicked()
                                                print('Choose Vessel')
                                        else:
                                            communicator.send_unready()
                                    elif vessel_id != -1:
                                        return vessel_id
                                    else:
                                        button.is_clicked()

        if is_multiplayer:
            if communicator.all_ready():
                return vessel_id

        if timer != 0:
            timer -= 1

        screen.blit(map_blur_surf, (0, 0))

        buttons.update()
        pygame.display.update()
        clock.tick(fps)


def add_dot():
    global active_dots, is_multiplayer, vessel_id

    top = random.randint(0, 1)
    if top:
        right = random.randint(0, 1)
        if right:
            pos_x = int(1600 * screen_scalar_x)
            if aspect_ratio_16x9:
                pos_y = random.randint(0, int(200 * screen_scalar_y))
            else:
                pos_y = random.randint(0, int(200 * screen_scalar_y))
            dir_x = -1
            dir_y = 0.75
        else:
            if aspect_ratio_16x9:
                pos_x = random.randint(int(1400 * screen_scalar_x), int(1600 * screen_scalar_x))
            else:
                pos_x = random.randint(int(1400 * screen_scalar_x), int(1600 * screen_scalar_x))
            pos_y = 0
            dir_x = -1
            dir_y = 0.5
    else:
        left = random.randint(0, 1)
        if left:
            pos_x = 0
            if aspect_ratio_16x9:
                pos_y = random.randint(int(680 * screen_scalar_y), int(900 * screen_scalar_y))
            else:
                pos_y = random.randint(int(680 * screen_scalar_y), int(900 * screen_scalar_y))
            dir_x = 1
            dir_y = -0.5
        else:
            if aspect_ratio_16x9:
                pos_x = random.randint(0, int(200 * screen_scalar_x))
            else:
                pos_x = random.randint(0, int(35 * screen_scalar_x))
            pos_y = int(900 * screen_scalar_y)
            dir_x = 1
            dir_y = -1

    if is_multiplayer:
        host_ip = list(map(int, communicator.HOST.split('.')))
    else:
        host_ip = '10.0.0.0'
    port = random.randint(1024, 65535)
    init_delay = random.randint(0, 60)

    speed = vessel_id_to_name[vessel_id][1]

    dot_values = [pos_x, pos_y, black, dir_x, dir_y, speed, init_delay, port, host_ip]

    if is_multiplayer:
        send_thread = threading.Thread(target=communicator.send_dot, args=(dot_values,))
        send_thread.start()

    active_dots += 1
    dots.add(Dot(*dot_values))

    if is_multiplayer:
        send_thread.join()


def stage5():
    global is_multiplayer, active_dots, max_dots

    screen.blit(map_surf, (0, 0))
    pygame.display.update()

    pause = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if is_multiplayer:
                    communicator.kill()
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if is_multiplayer:
                    communicator.kill()

                active_dots = 0
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                pause = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pause = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if active_dots  < max_dots:
                    add_dot()

        if pause:
            continue

        screen.blit(map_surf, (0, 0))

        dots.draw(screen)
        dots.update()

        pygame.display.update()
        clock.tick(fps)


def build_player_measurement():
    global player_id, number_of_databases, vessel_id

    measurement = ''

    if is_multiplayer:
        match number_of_databases:
            case 1:
                sample = radar_sample[vessel_id]
                measurement += ' '.join(map(str,sample))

            case 2:
                if player_id == 1:
                    sample = radar_sample[vessel_id]
                    measurement += ' '.join(map(str, sample))

                else:
                    sample = radar_sample[vessel_id]
                    measurement += ' '.join(map(str, sample))

            case 3:
                if player_id == 1:
                    sample = radar_sample[vessel_id]
                    measurement += ' '.join(map(str, sample))

                elif player_id == 2:
                    sample = radar_sample[vessel_id]
                    measurement += ' '.join(map(str, sample))

                else:
                    sample = radar_sample[vessel_id]
                    measurement += ' '.join(map(str, sample))
    else:
        sample = radar_sample[vessel_id]
        measurement += ' '.join(map(str,sample))


    with open(settings.measurement_input + '-P0-0', 'w') as f:
        f.write(measurement + '\n')

if __name__ == '__main__':
    port = 9000
    ip = '10.0.0.10'

    while True:
        antenna = Antenna()
        dots = pygame.sprite.Group()
        max_dots = 1
        active_dots = 0
        shares = max_dots
        max_shares = shares
        communicator = None

        buttons = pygame.sprite.Group()
        is_multiplayer = stage1()
        if not is_multiplayer:
            number_of_databases = stage2()
            if number_of_databases == -1:
                continue

        else:
            number_of_databases, player_id = stage3()
            if number_of_databases == -1:
                continue

        while True:
            vessel_id = stage4()
            if vessel_id == -1:
                break
            build_player_measurement()

            stage5()
