#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : yk
# @Time    : 2024/11/27 16:18
# @Name    : tif2png.py


try:
    import gdal
except:
    from osgeo import gdal
import os
import cv2


def TIFToPNG(tifDir_path, pngDir_path):
    if not os.path.exists(pngDir_path):
        os.makedirs(pngDir_path)
    for fileName in os.listdir(tifDir_path):
        if fileName[-4:] == ".tif":
            ds = gdal.Open(tifDir_path + "\\" + fileName)
            driver = gdal.GetDriverByName('PNG')
            driver.CreateCopy(pngDir_path + "\\" + fileName[:-4] + ".png", ds)
            print("已生成：", pngDir_path + "\\" + fileName[:-4] + ".png")


def TIFToJPG(tifDir_path, jpgDir_path):
    if not os.path.exists(jpgDir_path):
        os.makedirs(jpgDir_path)
    for fileName in os.listdir(tifDir_path):
        if fileName[-4:] == ".tif":
            ds = gdal.Open(tifDir_path + "\\" + fileName)
            driver = gdal.GetDriverByName('JPEG')
            output_file_path = os.path.join(jpgDir_path, fileName.replace('.tif', '.jpg'))
            driver.CreateCopy(output_file_path, ds)
            print("已生成：", output_file_path)

def TIFToPNG2(tifDir_path, pngDir_path):
    for imageName in os.listdir(tifDir_path):
        print("imageName", imageName)
        imagePath = os.path.join(tifDir_path, imageName)
        print("imagePath", imagePath)
        img = cv2.imread(imagePath)
        try:
            img.shape
        except:
            print('读取图片失败')
            break

        print("imageName.split('.')[0]", imageName.split('.')[0])
        distImagePath = os.path.join(pngDir_path, imageName.split('.')[0] + '_1.png')  # 更改图像后缀为.jpg，并保证与原图像同名
        print("distImagePath", distImagePath)
        cv2.imwrite(distImagePath, img)


if __name__ == '__main__':
    tifDir_path = r"F:\A-dataset-base\open-pit-mine-p10-slice\test_tif_2_png\in"
    pngDir_path = r"F:\A-dataset-base\open-pit-mine-p10-slice\test_tif_2_png"
    TIFToPNG2(tifDir_path, pngDir_path)
    TIFToJPG(tifDir_path, pngDir_path)