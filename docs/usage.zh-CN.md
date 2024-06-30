# 用法
## 基本介绍
```shell
python rpgmvtransl.py -d $original_data -s $rpgmaker_script -g $galtransl_script -t $translated_data [-e]
```
- 参数
  - `-d`, `--data`: 游戏的`data`文件夹路径。
  - `-s`, `--rpgmaker-script`: 初步提取出来的脚本的路径。
  - `-g`, `--galtransl-script`: [GalTransl](GalTranslRepo)的输入或输出。通常是`gt_input`或`gt_input`。
  - `-t`, `--translated-data`: 游戏数据文件的输出路径。

## 使用步骤
```shell
# 提取游戏数据
python rpgmvtransl.py extract -d /Game/RPGMakerMX/example/www/data -s /working/sdata

# 导出数据给GalTransl翻译
python rpgmvtransl.py galtransl -s /working/sdata -g /working/rpgmx-galtransl/gt_input
python galtransl/run_GalTransl.py /working/rpgmx-galtransl/config.yaml galtransl-v1

# 注入GalTransl的翻译到游戏数据里
python rpgmvtransl.py -d /Game/RPGMakerMX/example/www/data -s /working/sdata -g /working/rpgmx-galtransl/gt_output -t /working/tdata

# 复制翻译了的数据文件到游戏目录（记得先创建一个备份）
cp -r /Game/RPGMakerMX/example/www/data /Game/RPGMakerMX/example/www/data.bak
cp -rf /working/tdata /Game/RPGMakerMX/example/www/data
```

[GalTranslRepo]: https://github.com/XD2333/GalTransl