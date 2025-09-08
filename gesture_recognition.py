#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于MediaPipe的高精度手势识别系统
使用Google MediaPipe框架实现实时手势检测和控制
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Dict, List, Tuple
import math
from PIL import Image, ImageDraw, ImageFont
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GestureType(Enum):
    """手势类型枚举"""
    NONE = "none"
    FIST = "fist"  # 拳头
    OPEN_PALM = "open_palm"  # 张开手掌
    PEACE = "peace"  # V手势
    THUMBS_UP = "thumbs_up"  # 拇指向上
    POINTING_UP = "pointing_up"  # 食指向上
    THREE_FINGERS = "three_fingers"  # 三个手指
    TWO_FINGERS = "two_fingers"  # 两个手指
    ONE_FINGER = "one_finger"  # 一个手指

@dataclass
class GestureCommand:
    """手势命令配置"""
    gesture_type: GestureType
    action: str
    description: str
    hand_type: str = "both"  # "left", "right", "both"

class MediaPipeHandDetector:
    """MediaPipe手部检测器"""
    
    def __init__(self, 
                 static_image_mode=False,
                 max_num_hands=2,
                 min_detection_confidence=0.7,
                 min_tracking_confidence=0.5):
        """
        初始化MediaPipe手部检测器
        
        Args:
            static_image_mode: 是否为静态图像模式
            max_num_hands: 最大检测手数
            min_detection_confidence: 最小检测置信度
            min_tracking_confidence: 最小跟踪置信度
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # 手指关键点ID
        self.tip_ids = [4, 8, 12, 16, 20]  # 拇指、食指、中指、无名指、小指的指尖
        self.pip_ids = [3, 6, 10, 14, 18]  # 对应的PIP关节
        
    def detect_hands(self, image):
        """
        检测图像中的手部
        
        Args:
            image: 输入图像
            
        Returns:
            tuple: (处理后的图像, 手部检测结果)
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        return image, results
    
    def draw_landmarks(self, image, results):
        """
        在图像上绘制手部关键点
        
        Args:
            image: 输入图像
            results: 手部检测结果
        """
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
    
    def get_finger_positions(self, landmarks):
        """
        获取手指位置信息
        
        Args:
            landmarks: 手部关键点
            
        Returns:
            list: 每个手指是否伸直的状态 [拇指, 食指, 中指, 无名指, 小指]
        """
        fingers = []
        
        # 拇指 (特殊处理，因为拇指的方向不同)
        if landmarks[self.tip_ids[0]].x > landmarks[self.tip_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # 其他四个手指
        for i in range(1, 5):
            if landmarks[self.tip_ids[i]].y < landmarks[self.pip_ids[i]].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def calculate_distance(self, p1, p2):
        """
        计算两点之间的距离
        
        Args:
            p1, p2: 两个关键点
            
        Returns:
            float: 距离
        """
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

class GestureClassifier:
    """手势分类器"""
    
    def __init__(self):
        self.detector = MediaPipeHandDetector()
        
    def classify_gesture(self, landmarks) -> GestureType:
        """
        基于手部关键点分类手势
        
        Args:
            landmarks: 手部关键点
            
        Returns:
            GestureType: 识别的手势类型
        """
        fingers = self.detector.get_finger_positions(landmarks)
        fingers_up = sum(fingers)
        
        # 根据伸直的手指数量和模式判断手势
        if fingers_up == 0:
            return GestureType.FIST
        elif fingers_up == 5:
            return GestureType.OPEN_PALM
        elif fingers_up == 1:
            if fingers[1] == 1:  # 只有食指伸直
                return GestureType.POINTING_UP
            elif fingers[0] == 1:  # 只有拇指伸直
                return GestureType.THUMBS_UP
            else:
                return GestureType.ONE_FINGER
        elif fingers_up == 2:
            if fingers[1] == 1 and fingers[2] == 1:  # 食指和中指
                return GestureType.PEACE
            else:
                return GestureType.TWO_FINGERS
        elif fingers_up == 3:
            return GestureType.THREE_FINGERS
        elif fingers_up == 4:
            return GestureType.NONE
        
        return GestureType.NONE

class GestureController:
    """手势控制器"""
    
    def __init__(self):
        self.classifier = GestureClassifier()
        self.gesture_callbacks: Dict[str, Callable] = {}
        self.last_gesture = GestureType.NONE
        self.gesture_start_time = 0
        self.gesture_hold_duration = 2.0  # 手势保持时间（秒）
        self.frame_count = 0
        self.executed_gestures = set()  # 记录已执行的手势，避免重复执行
        self.running = False
        self.cap = None
        self.display_thread = None
        
        # 初始化中文字体
        self.font = self._init_chinese_font()
        
        # 帧计数器
        self.frame_count = 0
        
        # 手势命令映射
        self.gesture_commands = {
            GestureType.FIST: GestureCommand(
                GestureType.FIST, "close_all", "拳头 - 关闭所有设备"
            ),
            GestureType.OPEN_PALM: GestureCommand(
                GestureType.OPEN_PALM, "open_all", "张开手掌 - 打开所有设备"
            ),
            GestureType.PEACE: GestureCommand(
                GestureType.PEACE, "toggle_device", "V手势 - 切换设备状态"
            ),
            GestureType.THUMBS_UP: GestureCommand(
                GestureType.THUMBS_UP, "increase_brightness", "拇指向上 - 增加亮度"
            ),
            GestureType.POINTING_UP: GestureCommand(
                GestureType.POINTING_UP, "max_brightness", "食指向上 - 最大亮度"
            )
        }
        
        # 左右手特定命令映射
        self.left_hand_commands = {
            GestureType.THUMBS_UP: GestureCommand(
                GestureType.THUMBS_UP, "decrease_brightness", "左手拇指向上 - 降低亮度"
            ),
            GestureType.POINTING_UP: GestureCommand(
                GestureType.POINTING_UP, "min_brightness", "左手食指向上 - 最小亮度"
            ),
            GestureType.THREE_FINGERS: GestureCommand(
                GestureType.THREE_FINGERS, "decrease_color_temp", "左手三指 - 降低色温(暖光)"
            ),
            GestureType.TWO_FINGERS: GestureCommand(
                GestureType.TWO_FINGERS, "set_warm_color_temp", "左手两指 - 设置暖光色温"
            )
        }
        
        self.right_hand_commands = {
            GestureType.THUMBS_UP: GestureCommand(
                GestureType.THUMBS_UP, "increase_brightness", "右手拇指向上 - 增加亮度"
            ),
            GestureType.POINTING_UP: GestureCommand(
                GestureType.POINTING_UP, "max_brightness", "右手食指向上 - 最大亮度"
            ),
            GestureType.THREE_FINGERS: GestureCommand(
                GestureType.THREE_FINGERS, "increase_color_temp", "右手三指 - 提高色温(冷光)"
            ),
            GestureType.TWO_FINGERS: GestureCommand(
                GestureType.TWO_FINGERS, "set_cool_color_temp", "右手两指 - 设置冷光色温"
            )
        }
        
        # 手势名称映射
        self.gesture_names = {
            GestureType.NONE: "无手势",
            GestureType.FIST: "拳头",
            GestureType.OPEN_PALM: "张开手掌",
            GestureType.PEACE: "V手势",
            GestureType.THUMBS_UP: "拇指向上",
            GestureType.POINTING_UP: "食指向上",
            GestureType.THREE_FINGERS: "三个手指",
            GestureType.TWO_FINGERS: "两个手指",
            GestureType.ONE_FINGER: "一个手指"
        }
    
    def _init_chinese_font(self):
        """初始化中文字体"""
        try:
            # 尝试使用系统字体
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/simkai.ttf",  # 楷体
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, 20)
            
            # 如果没有找到中文字体，使用默认字体
            logger.warning("未找到中文字体，使用默认字体")
            return ImageFont.load_default()
        except Exception as e:
            logger.error(f"字体初始化失败: {e}")
            return ImageFont.load_default()
    
    def register_gesture_callback(self, gesture_key: str, callback: Callable):
        """注册手势回调函数"""
        self.gesture_callbacks[gesture_key] = callback
        logger.info(f"已注册手势回调: {gesture_key}")
    
    def start(self, camera_index: int = 0) -> bool:
        """启动手势识别"""
        try:
            if self.running:
                return True
            
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                logger.error("无法打开摄像头")
                return False
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.running = True
            logger.info("手势识别启动成功")
            
            # 启动显示循环
            import threading
            self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
            self.display_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"启动手势识别失败: {e}")
            return False
    
    def stop(self):
        """停止手势识别"""
        try:
            self.running = False
            if self.cap:
                self.cap.release()
                self.cap = None
            cv2.destroyAllWindows()
            logger.info("手势识别已停止")
        except Exception as e:
            logger.error(f"停止手势识别失败: {e}")
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.running
    
    def _display_loop(self):
        """显示循环"""
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                logger.error("无法读取摄像头画面")
                break
            
            # 水平翻转画面
            frame = cv2.flip(frame, 1)
            
            # 处理手势识别
            processed_frame = self.process_frame(frame)
            
            # 显示画面
            cv2.imshow('手势识别', processed_frame)
            
            # 检查退出键
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # q键或ESC键退出
                break
        
        # 清理资源
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.running = False
        logger.info("显示循环已结束")
    
    def process_frame(self, frame):
        """
        处理视频帧并识别手势
        
        Args:
            frame: 输入视频帧
            
        Returns:
            tuple: (处理后的帧, 当前手势)
        """
        self.frame_count += 1
        
        # 检测手部
        frame, results = self.classifier.detector.detect_hands(frame)
        current_gesture = GestureType.NONE
        hand_type = "unknown"
        
        if results.multi_hand_landmarks and results.multi_handedness:
            # 绘制手部关键点
            self.classifier.detector.draw_landmarks(frame, results)
            
            # 处理每只检测到的手
            for i, (hand_landmarks, handedness) in enumerate(
                zip(results.multi_hand_landmarks, results.multi_handedness)):
                
                # 获取手的类型（左手/右手）
                hand_label = handedness.classification[0].label
                hand_type = "left" if hand_label == "Left" else "right"
                
                # 分类手势
                gesture = self.classifier.classify_gesture(hand_landmarks.landmark)
                
                if gesture != GestureType.NONE:
                    current_gesture = gesture
                    break
        
        # 处理手势逻辑
        self._handle_gesture_logic(current_gesture, hand_type)
        
        # 绘制界面信息
        self._draw_interface(frame, current_gesture, hand_type)
        
        return frame
    
    def _handle_gesture_logic(self, gesture: GestureType, hand_type: str):
        """处理手势逻辑"""
        current_time = time.time()
        
        # 直接执行手势，无需确认模式
        if gesture != GestureType.NONE and gesture in self.gesture_commands:
            if gesture != self.last_gesture:
                self.gesture_start_time = current_time
                self.last_gesture = gesture
                # 清除已执行手势记录
                if gesture in self.executed_gestures:
                    self.executed_gestures.remove(gesture)
            elif current_time - self.gesture_start_time >= self.gesture_hold_duration:
                # 手势保持足够时间，直接执行
                if gesture not in self.executed_gestures:
                    self._execute_gesture(gesture, hand_type)
                    self.executed_gestures.add(gesture)
        else:
            self.last_gesture = GestureType.NONE
    
    def _execute_gesture(self, gesture: GestureType, hand_type: str):
        """执行手势"""
        # 根据左右手选择不同的命令映射
        command = None
        
        if hand_type == "left" and gesture in self.left_hand_commands:
            command = self.left_hand_commands[gesture]
        elif hand_type == "right" and gesture in self.right_hand_commands:
            command = self.right_hand_commands[gesture]
        elif gesture in self.gesture_commands:
            command = self.gesture_commands[gesture]
        
        if command:
            gesture_key = f"{hand_type}_{gesture.value}"
            callback = self.gesture_callbacks.get(gesture_key)
            
            if not callback:
                # 尝试通用回调
                callback = self.gesture_callbacks.get(command.action)
            
            if callback:
                try:
                    logger.info(f"执行手势: {command.description}")
                    callback()
                except Exception as e:
                    logger.error(f"执行手势回调时出错: {e}")
    
    def _draw_interface(self, frame, current_gesture: GestureType, hand_type: str):
        """绘制界面信息"""
        height, width = frame.shape[:2]
        
        # 转换为PIL图像以支持中文显示
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        # 绘制当前手势
        gesture_text = self.gesture_names.get(current_gesture, "未知手势")
        if hand_type != "unknown":
            hand_text = "左手" if hand_type == "left" else "右手"
            gesture_text = f"{hand_text}: {gesture_text}"
        
        current_text = f"当前手势: {gesture_text}"
        draw.text((10, 10), current_text, font=self.font, fill=(0, 255, 0))
        
        # 绘制手势保持状态
        if self.last_gesture != GestureType.NONE and self.last_gesture in self.gesture_commands:
            current_time = time.time()
            hold_time = current_time - self.gesture_start_time
            remaining_time = max(0, self.gesture_hold_duration - hold_time)
            
            if remaining_time > 0:
                gesture_name = self.gesture_names.get(self.last_gesture, "未知")
                progress_text = f"保持手势 {gesture_name}: {remaining_time:.1f}s"
                draw.text((10, height - 80), progress_text, font=self.font, fill=(255, 165, 0))
            elif self.last_gesture not in self.executed_gestures:
                execute_text = f"执行手势: {self.gesture_names.get(self.last_gesture, '未知')}"
                draw.text((10, height - 80), execute_text, font=self.font, fill=(0, 255, 0))
        
        # 绘制支持的手势列表
        y_offset = 50
        draw.text((10, y_offset), "支持的手势:", font=self.font, fill=(255, 255, 255))
        
        # 通用手势
        y_offset += 30
        draw.text((10, y_offset), "通用手势 (左右手通用):", font=self.font, fill=(255, 255, 0))
        y_offset += 25
        draw.text((10, y_offset), "• 拳头 - 关闭所有设备", font=self.font, fill=(255, 255, 255))
        y_offset += 25
        draw.text((10, y_offset), "• 张开手掌 - 打开所有设备", font=self.font, fill=(255, 255, 255))
        y_offset += 25
        draw.text((10, y_offset), "• V手势 - 切换设备状态", font=self.font, fill=(255, 255, 255))
        
        # 右手专用手势
        y_offset += 35
        draw.text((10, y_offset), "右手专用手势:", font=self.font, fill=(0, 255, 255))
        y_offset += 25
        draw.text((10, y_offset), "• 右手拇指向上 - 增加亮度", font=self.font, fill=(255, 255, 255))
        y_offset += 25
        draw.text((10, y_offset), "• 右手食指向上 - 最大亮度", font=self.font, fill=(255, 255, 255))
        
        # 左手专用手势
        y_offset += 35
        draw.text((10, y_offset), "左手专用手势:", font=self.font, fill=(255, 0, 255))
        y_offset += 25
        draw.text((10, y_offset), "• 左手拇指向上 - 降低亮度", font=self.font, fill=(255, 255, 255))
        y_offset += 25
        draw.text((10, y_offset), "• 左手食指向上 - 最小亮度", font=self.font, fill=(255, 255, 255))
        
        # 绘制帧数和退出提示
        draw.text((width - 150, 10), f"累计帧数: {self.frame_count}", font=self.font, fill=(255, 255, 255))
        draw.text((10, height - 25), "按 'q' 退出", font=self.font, fill=(255, 255, 255))
        
        # 转换回OpenCV格式
        frame[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def main():
    """主函数"""
    # 导入设备控制器
    try:
        from device_controller import DeviceController
        device_controller = DeviceController()
        logger.info("设备控制器加载成功")
    except ImportError:
        logger.warning("无法导入设备控制器，使用模拟功能")
        device_controller = None
    
    # 创建手势控制器
    gesture_controller = GestureController()
    
    # 注册手势回调函数
    def create_device_callback(action):
        def callback():
            if device_controller:
                if action == "close_all":
                    result = device_controller.turn_off_all()
                    logger.info(f"关闭所有设备结果: {result}")
                elif action == "open_all":
                    result = device_controller.turn_on_all()
                    logger.info(f"打开所有设备结果: {result}")
                elif action == "toggle_device":
                    # 简单实现：获取第一个设备并切换状态
                    devices = device_controller.get_all_devices()
                    if devices:
                        device_name = list(devices.keys())[0]
                        device = devices[device_name]
                        if hasattr(device, 'device_info') and device.device_info.power:
                            device.turn_off()
                            logger.info(f"关闭设备: {device_name}")
                        else:
                            device.turn_on()
                            logger.info(f"打开设备: {device_name}")
                elif action == "max_brightness":
                    result = device_controller.adjust_brightness_all(100)
                    logger.info(f"设置最大亮度结果: {result}")
                elif action == "increase_brightness":
                    result = device_controller.adjust_brightness_all(20)
                    logger.info(f"增加亮度结果: {result}")
            else:
                logger.info(f"模拟执行: {action}")
        return callback
    
    # 注册左右手手势回调
    for hand in ["left", "right"]:
        for gesture_type, command in gesture_controller.gesture_commands.items():
            callback_key = f"{hand}_{gesture_type.value}"
            gesture_controller.register_gesture_callback(
                callback_key, create_device_callback(command.action)
            )
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    # 设置摄像头参数
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    logger.info("手势识别已启动")
    logger.info("支持的手势:")
    for gesture_type, command in gesture_controller.gesture_commands.items():
        logger.info(f"  {command.description}")
    
    logger.info("如果看不到摄像头窗口，请检查：")
    logger.info("1. 窗口是否被其他程序遮挡")
    logger.info("2. 任务栏是否有OpenCV窗口")
    logger.info("3. 按Alt+Tab查看所有窗口")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("无法读取摄像头帧")
                break
            
            # 水平翻转图像（镜像效果）
            frame = cv2.flip(frame, 1)
            
            # 处理手势识别
            processed_frame, current_gesture = gesture_controller.process_frame(frame)
            
            # 显示结果
            cv2.imshow('MediaPipe Hand Gesture Recognition', processed_frame)
            
            # 按'q'退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # 每100帧输出一次状态
            if gesture_controller.frame_count % 100 == 0:
                logger.info(f"已处理 {gesture_controller.frame_count} 帧，当前手势: {current_gesture.value}")
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        # 清理资源
        cap.release()
        cv2.destroyAllWindows()
        logger.info("手势识别已停止")

if __name__ == "__main__":
    main()