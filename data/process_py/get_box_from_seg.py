#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : yk
# @Time    : 2024/11/25 16:49
# @Name    : get_box_from_seg.py

import cv2
import os
import numpy as np

# 定义类别标签
background_label = 1
object_label = 0

# 输入文件夹和输出文件夹
input_folder = r"F:\A-dataset-base\Potsdam2410302\241125-test-label-conver2yolo\input"
output_folder = r"F:\A-dataset-base\Potsdam2410302\241125-test-label-conver2yolo\output" + '\\'
count = 1
# 获取输入文件夹中的所有标签图像文件名
image_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]


def extract_number(filename):
    # 提取文件名中的数字部分
    return int(''.join(filter(str.isdigit, filename)))


image_files = sorted(os.listdir(input_folder), key=extract_number)


#读入DSM
# a_dsm_image = cv2.imread(r"F:\A-dataset-base\Potsdam2410302\1_DSM\dsm_potsdam_04_11.tif", cv2.IMREAD_ANYDEPTHIMREAD_ANYDEPTH)


# 黑色，白色，黄色(255,255,0)（车辆），绿色(0,255,0)，红色rgb(255,0,0)，蓝色rgb(0,0,255),浅蓝色rgb(0,255,255)
rgbmask = np.array([[0,0,0],[255,255,255],[255,255,0]],dtype=np.uint8)
# 遍历每个标签图像文件
for image_file in image_files:
    print(image_file)
    # 读取语义分割图像
    image_path = os.path.join(input_folder, image_file)
    semantic_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # 采坑，很重要，tif格式必须转一下，要不然颜色不对
    semantic_image = cv2.cvtColor(semantic_image, cv2.COLOR_BGR2RGB)

    my_mask = np.zeros((semantic_image.shape[0], semantic_image.shape[1]), dtype=np.uint8)
    my_mask[np.where(np.all(semantic_image == rgbmask[2], axis=-1))[:2]] = 1

    yellow_only = cv2.bitwise_and(semantic_image, semantic_image, mask=my_mask)
    # # 绘制
    # cv2.namedWindow('mask2', cv2.WINDOW_KEEPRATIO)
    # cv2.imshow('mask2', cv2.cvtColor(yellow_only, cv2.COLOR_RGB2BGR))
    # cv2.namedWindow('raw-img', cv2.WINDOW_KEEPRATIO)
    # cv2.imshow('raw-img',  cv2.cvtColor(semantic_image, cv2.COLOR_RGB2BGR))
    # cv2.waitKey(0)


    # # 将红色区域标记为目标区域
    # object_mask = (semantic_image[:, :, 2] == 255) & (semantic_image[:, :, 0] == 255) & (semantic_image[:, :, 1] == 0)
    # cv2.imshow("mask2", object_mask.astype(np.uint8)*255)
    # cv2.waitKey(0)
    # cv2.imshow('mask1', object_mask)





    # print(object_mask)
    # 寻找目标区域的轮廓
    contours, _ = cv2.findContours(my_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(contours)
    # 定义输出文件路径
    output_path = "{}img{}.txt".format(output_folder, count)
    count += 1



    # 将目标信息保存到txt文件中
    with open(output_path, "w") as f:
        for contour in contours:
            # 计算目标的边界框
            x, y, w, h = cv2.boundingRect(contour)

            # 绘制方框
            box1 = np.array([[[x, y]], [[x + w, y]], [[x + w, y + h]], [[x, y + h]]])
            cv2.drawContours(yellow_only, [box1], -1, (255, 255, 255), 2)
            # 在原图像上绘制轮廓
            cv2.drawContours(yellow_only, contour, -1, (255, 0, 0), 3)


            # 计算边界框的中心坐标和归一化坐标
            center_x = (x + w / 2) / semantic_image.shape[1]
            center_y = (y + h / 2) / semantic_image.shape[0]
            normalized_w = w / semantic_image.shape[1]
            normalized_h = h / semantic_image.shape[0]

            # 写入YOLO格式的标签信息到txt文件
            line = f"{object_label} {center_x:.6f} {center_y:.6f} {normalized_w:.6f} {normalized_h:.6f}\n"
            f.write(line)
    # 最后绘制
    out_pic = cv2.cvtColor(yellow_only, cv2.COLOR_RGB2BGR)
    cv2.namedWindow('mask2', cv2.WINDOW_KEEPRATIO)
    cv2.imshow('mask2', out_pic)
    # 写入tif文件汇总试试
    output_path_tif = "{}img{}.tif".format(output_folder, count)
    cv2.imwrite(output_path_tif, out_pic)
    # cv2.namedWindow('raw-img', cv2.WINDOW_KEEPRATIO)
    # cv2.imshow('raw-img',  cv2.cvtColor(semantic_image, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    print(f"Processed: {image_file}")

print("Batch processing completed.")