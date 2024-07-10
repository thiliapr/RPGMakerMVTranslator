# 用法
## 基本介绍
```shell
python rpgmvtransl.py -d $original_data -s $rpgmaker_script -t $translated_data
```
- 参数
  - `-d`, `--data`: 游戏的`data`文件夹路径。
  - `-s`, `--rpgmaker-script`: 初步提取出来的脚本的路径。
  - `-t`, `--translated-data`: 游戏数据文件的输出路径。

## 使用步骤
1. 提取游戏数据。
2. 导出数据给[TkTransl][TkTranslRepo]翻译。
3. 将翻译注入到游戏数据。
4. 复制数据到游戏目录，覆盖原文件。（最好先创建备份）

```shell
# 提取游戏数据
python rpgmvtransl.py extract -d /Game/RPGMakerMX/example/www/data -s /working/sdata

# 复制数据给TkTransl翻译
cp /working/sdata /tktransl/projects/example/input
python /tktransl/tktransl.py example galtransl-v1

# 注入GalTransl的翻译到游戏数据里
python rpgmvtransl.py -d /Game/RPGMakerMX/example/www/data -s /tktransl/projects/example/output -t /working/tdata

# 复制翻译了的数据文件到游戏目录（记得先创建一个备份）
cp -r /Game/RPGMakerMX/example/www/data /Game/RPGMakerMX/example/www/data.bak
cp -rf /working/tdata /Game/RPGMakerMX/example/www/data
```

[TkTranslRepo]: https://github.com/thiliapr/TkTransl