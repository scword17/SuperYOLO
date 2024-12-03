#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : yk
# @Time    : 2024/11/26 19:24
# @Name    : cut_tif.py


import os
import sys
try:
    import gdal
except:
    from osgeo import gdal
import numpy as np
from PIL import Image



# 保存tif文件函数
def writeTiff(im_data, im_geotrans, im_proj, path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
        im_bands, im_height, im_width = im_data.shape
    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    # if (dataset != None):
    #     dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
    #     dataset.SetProjection(im_proj)  # 写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset



# 像素坐标和地理坐标仿射变换
def CoordTransf(Xpixel, Ypixel, GeoTransform):
    XGeo = GeoTransform[0] + GeoTransform[1] * Xpixel + Ypixel * GeoTransform[2]
    YGeo = GeoTransform[3] + GeoTransform[4] * Xpixel + Ypixel * GeoTransform[5]
    return XGeo, YGeo


'''
滑动窗口裁剪Tif影像
TifPath 影像路径
SavePath 裁剪后影像保存目录
CropSize 裁剪尺寸
RepetitionRate 重叠度
'''
def TifCrop(TifPath, SavePath, CropSize, RepetitionRate):
    print("--------------------裁剪影像-----------------------")
    CropSize = int(CropSize)
    RepetitionRate = float(RepetitionRate)
    dataset_img = gdal.Open(TifPath)
    if dataset_img == None:
        print(TifPath + "文件无法打开")

    if not os.path.exists(SavePath):
        os.makedirs(SavePath)

    width = dataset_img.RasterXSize     # 获取行列数
    height = dataset_img.RasterYSize
    bands = dataset_img.RasterCount  # 获取波段数
    print("行数为：", height)
    print("列数为：", width)
    print("波段数为：", bands)

    proj = dataset_img.GetProjection()      # 获取投影信息
    geotrans = dataset_img.GetGeoTransform()        # 获取仿射矩阵信息
    img = dataset_img.ReadAsArray(0, 0, width, height)  # 获取数据

    #  行上图像块数目
    RowNum = int((height - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))
    #  列上图像块数目
    ColumnNum = int((width - CropSize * RepetitionRate) / (CropSize * (1 - RepetitionRate)))
    print("裁剪后行影像数为：", RowNum)
    print("裁剪后列影像数为：", ColumnNum)

    # 获取当前文件夹的文件个数len,并以len+1命名即将裁剪得到的图像
    new_name = len(os.listdir(SavePath)) + 1

    # 裁剪图片,重复率为RepetitionRate
    for i in range(RowNum):
        for j in range(ColumnNum):
            # 如果图像是单波段
            if (bands == 1):
                cropped = img[
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            # 如果图像是多波段
            else:
                cropped = img[:,
                          int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                          int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
            # 获取地理坐标
            XGeo, YGeo = CoordTransf(int(j * CropSize * (1 - RepetitionRate)),
                                     int(i * CropSize * (1 - RepetitionRate)),
                                     geotrans)
            crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])

            # 生成Tif图像
            writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)

            # 文件名 + 1
            new_name = new_name + 1
    # 向前裁剪最后一行
    for i in range(RowNum):
        if (bands == 1):
            cropped = img[int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]
        else:
            cropped = img[:,
                      int(i * CropSize * (1 - RepetitionRate)): int(i * CropSize * (1 - RepetitionRate)) + CropSize,
                      (width - CropSize): width]
        # 获取地理坐标
        XGeo, YGeo = CoordTransf(width - CropSize,
                                 int(i * CropSize * (1 - RepetitionRate)),
                                 geotrans)
        crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])

        # 生成Tif影像
        writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)

        new_name = new_name + 1
    # 向前裁剪最后一列
    for j in range(ColumnNum):
        if (bands == 1):
            cropped = img[(height - CropSize): height,
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        else:
            cropped = img[:,
                      (height - CropSize): height,
                      int(j * CropSize * (1 - RepetitionRate)): int(j * CropSize * (1 - RepetitionRate)) + CropSize]
        # 获取地理坐标
        XGeo, YGeo = CoordTransf(int(j * CropSize * (1 - RepetitionRate)),
                                 height - CropSize,
                                 geotrans)
        crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])
        # 生成tif影像
        writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)

        # 文件名 + 1
        new_name = new_name + 1
    # 裁剪右下角
    if (bands == 1):
        cropped = img[(height - CropSize): height,
                  (width - CropSize): width]
    else:
        cropped = img[:,
                  (height - CropSize): height,
                  (width - CropSize): width]

    XGeo, YGeo = CoordTransf(width - CropSize,
                             height - CropSize,
                             geotrans)
    crop_geotrans = (XGeo, geotrans[1], geotrans[2], YGeo, geotrans[4], geotrans[5])
    # 生成Tif影像
    writeTiff(cropped, crop_geotrans, proj, SavePath + "/%d.tif" % new_name)

    new_name = new_name + 1


if __name__ == '__main__':
    # 将影像裁剪为重复率为0.3的2048×2048的数据集
    TifCrop(r"F:\A-dataset-base\Potsdam2410302\241125-test-label-conver2yolo\input\top_potsdam_2_12_label.tif",
            r"F:\A-dataset-base\Potsdam2410302\241125-test-label-conver2yolo\cutout3", 1024, 0)

